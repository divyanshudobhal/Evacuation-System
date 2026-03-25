document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transform = 'translateX(100%)';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate__animated', 'animate__fadeInUp');
    });

    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
        });
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<div class="loading"></div> Processing...';
                submitBtn.disabled = true;
            }
        });
    });

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .stat-card, .card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
});

class EvacuationMap {
    constructor(containerId, width, height) {
        this.container = document.getElementById(containerId);
        this.width = width;
        this.height = height;
        this.grid = [];
        this.start = null;
        this.end = null;
        this.hazards = new Map();
        this.selectedHazardType = 'fire';
        this.path = null;
        this.initializeGrid();
    }

    initializeGrid() {
        this.container.innerHTML = '';
        this.container.style.gridTemplateColumns = `repeat(${this.width}, 1fr)`;
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                const cell = document.createElement('div');
                cell.className = 'grid-cell';
                cell.dataset.x = x;
                cell.dataset.y = y;
                cell.textContent = '';
                cell.addEventListener('click', () => this.handleCellClick(x, y));
                cell.addEventListener('contextmenu', (e) => {
                    e.preventDefault();
                    this.handleRightClick(x, y);
                });
                cell.style.animationDelay = `${(x + y) * 0.05}s`;
                cell.classList.add('animate__animated', 'animate__fadeIn');
                this.container.appendChild(cell);
            }
        }
    }

    handleCellClick(x, y) {
        const key = `${x},${y}`;
        if (!this.start) {
            this.setStart(x, y);
        } else if (!this.end && !this.hazards.has(key)) {
            this.setEnd(x, y);
        } else {
            this.toggleHazard(x, y);
        }
    }

    handleRightClick(x, y) {
        const key = `${x},${y}`;
        if (this.hazards.has(key)) {
            this.removeHazard(x, y);
        } else if (this.start && this.start.x === x && this.start.y === y) {
            this.start = null;
            this.updateDisplay();
        } else if (this.end && this.end.x === x && this.end.y === y) {
            this.end = null;
            this.updateDisplay();
        }
    }

    setStart(x, y) {
        this.start = { x, y };
        this.animateCell(x, y, 'start');
        this.updateDisplay();
    }

    setEnd(x, y) {
        this.end = { x, y };
        this.animateCell(x, y, 'end');
        this.updateDisplay();
    }

    animateCell(x, y, type) {
        const cell = this.getCell(x, y);
        if (cell) {
            cell.classList.add('animate__animated', 'animate__pulse');
            setTimeout(() => {
                cell.classList.remove('animate__animated', 'animate__pulse');
            }, 1000);
        }
    }

    getCell(x, y) {
        return this.container.querySelector(`[data-x="${x}"][data-y="${y}"]`);
    }

    toggleHazard(x, y) {
        const key = `${x},${y}`;
        if (this.hazards.has(key)) {
            this.removeHazard(x, y);
        } else {
            this.addHazard(x, y, this.selectedHazardType);
        }
    }

    addHazard(x, y, type) {
        const key = `${x},${y}`;
        this.hazards.set(key, { x, y, type, intensity: 1 });
        this.animateCell(x, y, 'hazard');
        fetch('/api/hazard', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                building_id: parseInt(document.getElementById('building-id').value),
                x: x,
                y: y,
                type: type,
                intensity: 1
            })
        });
        this.updateDisplay();
    }

    removeHazard(x, y) {
        const key = `${x},${y}`;
        this.hazards.delete(key);
        const cell = this.getCell(x, y);
        if (cell) {
            cell.classList.add('animate__animated', 'animate__fadeOut');
            setTimeout(() => {
                cell.classList.remove('animate__animated', 'animate__fadeOut');
                this.updateDisplay();
            }, 500);
        }
        fetch('/api/hazard', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                building_id: parseInt(document.getElementById('building-id').value),
                x: x,
                y: y
            })
        });
    }

    updateDisplay() {
        const cells = this.container.querySelectorAll('.grid-cell');
        cells.forEach(cell => {
            const x = parseInt(cell.dataset.x);
            const y = parseInt(cell.dataset.y);
            const key = `${x},${y}`;
            cell.className = 'grid-cell';
            cell.textContent = '';
            if (this.start && this.start.x === x && this.start.y === y) {
                cell.classList.add('start');
                cell.textContent = '🚩';
            } else if (this.end && this.end.x === x && this.end.y === y) {
                cell.classList.add('end');
                cell.textContent = '🏁';
            } else if (this.hazards.has(key)) {
                const hazard = this.hazards.get(key);
                cell.classList.add(`hazard-${hazard.type}`);
                const icons = {
                    'fire': '🔥',
                    'smoke': '💨',
                    'water': '💧',
                    'chemical': '☣️',
                    'blocked': '🚧'
                };
                cell.textContent = icons[hazard.type] || '⚠️';
            } else if (this.path && this.path.some(point => point[0] === x && point[1] === y)) {
                cell.classList.add('path');
                cell.textContent = '•';
            }
        });
    }

    async calculatePath() {
        if (!this.start || !this.end) {
            this.showNotification('Please set both start and end points', 'warning');
            return;
        }
        const calculateBtn = document.querySelector('button[onclick="window.evacuationMap.calculatePath()"]');
        const originalText = calculateBtn.innerHTML;
        try {
            calculateBtn.innerHTML = '<div class="loading"></div> Calculating...';
            calculateBtn.disabled = true;
            const response = await fetch('/api/path', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    building_id: parseInt(document.getElementById('building-id').value),
                    start_x: this.start.x,
                    start_y: this.start.y,
                    end_x: this.end.x,
                    end_y: this.end.y,
                    name: `Path ${new Date().toLocaleTimeString()}`
                })
            });
            const data = await response.json();
            if (data.success) {
                this.path = data.path;
                this.animatePath(this.path);
                this.updateDisplay();
                this.showNotification(`✅ Path found! Steps: ${data.steps}, Cost: ${data.cost.toFixed(2)}`, 'success');
            } else {
                this.showNotification(data.error, 'danger');
            }
        } catch (error) {
            console.error('Error calculating path:', error);
            this.showNotification('Error calculating path', 'danger');
        } finally {
            calculateBtn.innerHTML = originalText;
            calculateBtn.disabled = false;
        }
    }

    animatePath(path) {
        path.forEach((point, index) => {
            setTimeout(() => {
                const cell = this.getCell(point[0], point[1]);
                if (cell && !cell.classList.contains('start') && !cell.classList.contains('end')) {
                    cell.classList.add('animate__animated', 'animate__bounceIn');
                    setTimeout(() => {
                        cell.classList.remove('animate__animated', 'animate__bounceIn');
                    }, 1000);
                }
            }, index * 100);
        });
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        const container = document.getElementById('path-result') || document.body;
        container.innerHTML = '';
        container.appendChild(notification);
    }

    clearPath() {
        this.path = null;
        this.updateDisplay();
        document.getElementById('path-result').innerHTML = '';
        this.showNotification('Path cleared', 'info');
    }

    clearAll() {
        this.start = null;
        this.end = null;
        this.hazards.clear();
        this.path = null;
        fetch('/api/hazard/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                building_id: parseInt(document.getElementById('building-id').value)
            })
        }).catch(console.error);
        this.updateDisplay();
        this.showNotification('All cleared', 'info');
    }
}

if (document.getElementById('grid-map')) {
    const buildingWidth = parseInt(document.getElementById('building-width').value);
    const buildingHeight = parseInt(document.getElementById('building-height').value);
    window.evacuationMap = new EvacuationMap('grid-map', buildingWidth, buildingHeight);
}
