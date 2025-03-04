// Canvas setup
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const SCREEN_WIDTH = canvas.width;
const SCREEN_HEIGHT = canvas.height;

// Colors
const COLORS = {
    BLACK: '#000000',
    WHITE: '#FFFFFF',
    RED: '#FF0000',
    GREEN: '#00FF00',
    BLUE: '#0000FF',
    YELLOW: '#FFFF00',
    GRAY: '#323232',
    LIGHT_GRAY: '#646464'
};

// Game state
let gameState = 'playing';
let gameResult = null;

// Utility functions
function distance(x1, y1, x2, y2) {
    return Math.hypot(x2 - x1, y2 - y1);
}

// Player class
class Player {
    constructor() {
        this.x = SCREEN_WIDTH / 2;
        this.y = SCREEN_HEIGHT / 2;
        this.size = 30;
        this.speed = 300;
        this.health = 100;
        this.maxHealth = 100;
        this.experience = 0;
        this.level = 1;
        this.expToNextLevel = this.level;
        this.weapons = [new Gun(this), new BlobWeapon(this), new HeavyAttack(this)];
        this.killCount = 0;
        this.keys = {};
    }

    update(dt) {
        let vx = 0, vy = 0;
        if (this.keys['w'] || this.keys['ArrowUp']) vy -= this.speed;
        if (this.keys['s'] || this.keys['ArrowDown']) vy += this.speed;
        if (this.keys['a'] || this.keys['ArrowLeft']) vx -= this.speed;
        if (this.keys['d'] || this.keys['ArrowRight']) vx += this.speed;

        if (vx !== 0 || vy !== 0) {
            const mag = Math.sqrt(vx * vx + vy * vy);
            vx = (vx / mag) * this.speed * dt;
            vy = (vy / mag) * this.speed * dt;
        }

        this.x = Math.max(this.size / 2, Math.min(SCREEN_WIDTH - this.size / 2, this.x + vx));
        this.y = Math.max(this.size / 2, Math.min(SCREEN_HEIGHT - this.size / 2, this.y + vy));

        this.weapons.forEach(weapon => weapon.update(dt));
    }

    draw() {
        ctx.fillStyle = COLORS.WHITE;
        ctx.fillRect(this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
    }
}

// Enemy class
class Enemy {
    constructor(x, y, type = 'normal', playerLevel = 1) {
        this.x = x;
        this.y = y;
        this.type = type;
        this.size = type === 'boss' ? 70 : 20;
        if (type === 'normal') {
            this.color = COLORS.GREEN;
            this.speed = 70;
            this.health = 10 + playerLevel;
            this.damageRate = 20;
        } else if (type === 'fast') {
            this.color = COLORS.RED;
            this.speed = 200;
            this.health = 10 + playerLevel;
            this.damageRate = 10;
        } else if (type === 'strong') {
            this.color = COLORS.BLUE;
            this.speed = 50;
            this.health = 100 + 3 * playerLevel;
            this.damageRate = 30;
        } else if (type === 'boss') {
            this.color = COLORS.YELLOW;
            this.speed = 200;
            this.health = 500 + 10 * playerLevel;
            this.damageRate = 50;
        }
    }

    update(dt) {
        const dx = player.x - this.x;
        const dy = player.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist > 0) {
            this.x += (dx / dist) * this.speed * dt;
            this.y += (dy / dist) * this.speed * dt;
        }
    }

    draw() {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
    }
}

// Projectile class
class Projectile {
    constructor(x, y, dx, dy, damage, color, piercing = false) {
        this.x = x;
        this.y = y;
        this.size = 5;
        this.dx = dx * 500;
        this.dy = dy * 500;
        this.damage = damage;
        this.color = color;
        this.piercing = piercing;
        this.lifetime = 2;
        this.hitEnemies = new Set();
    }

    update(dt) {
        this.x += this.dx * dt;
        this.y += this.dy * dt;
        this.lifetime -= dt;
        if (this.lifetime <= 0 || !this.isOnScreen()) this.alive = false;
    }

    draw() {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
    }

    isOnScreen() {
        return this.x > 0 && this.x < SCREEN_WIDTH && this.y > 0 && this.y < SCREEN_HEIGHT;
    }
}

// Blob class
class Blob {
    constructor(x, y, damage, speed) {
        this.x = x;
        this.y = y;
        this.size = 20;
        this.damage = damage;
        this.speed = speed;
        this.angle = 0;
        this.distance = 100;
        this.hitEnemies = new Set();
    }

    update(dt) {
        this.angle += this.speed * dt;
        this.x = player.x + Math.cos(this.angle) * this.distance;
        this.y = player.y + Math.sin(this.angle) * this.distance;
        if (this.angle >= 2 * Math.PI) {
            this.hitEnemies.clear();
            this.angle -= 2 * Math.PI;
        }
    }

    draw() {
        ctx.fillStyle = COLORS.YELLOW;
        ctx.fillRect(this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
    }
}

// Item classes
class ExpItem {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = 10;
        this.value = 1;
    }

    draw() {
        ctx.fillStyle = COLORS.BLUE;
        ctx.fillRect(this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
    }
}

class HealthItem {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.size = 10;
        this.value = Math.floor(Math.random() * 10) + 1;
    }

    draw() {
        ctx.fillStyle = COLORS.GREEN;
        ctx.fillRect(this.x - this.size / 2, this.y - this.size / 2, this.size, this.size);
    }
}

// Weapon classes
class Gun {
    constructor(player) {
        this.player = player;
        this.name = 'Gun';
        this.level = 1;
        this.damage = 5 + this.level * 2;
        this.cooldown = 0.5 / this.level;
        this.timer = 0;
    }

    update(dt) {
        this.timer += dt;
        if (this.timer >= this.cooldown) {
            this.fire();
            this.timer = 0;
        }
    }

    fire() {
        const nearest = findNearestEnemy(this.player.x, this.player.y);
        if (nearest) {
            const dx = nearest.x - this.player.x;
            const dy = nearest.y - this.player.y;
            const mag = Math.sqrt(dx * dx + dy * dy);
            projectiles.push(new Projectile(this.player.x, this.player.y, dx / mag, dy / mag, this.damage, COLORS.RED));
        }
    }

    upgrade() {
        if (this.level < 10) {
            this.level++;
            this.damage = 5 + this.level * 2;
            this.cooldown = 0.5 / this.level;
        }
    }
}

class BlobWeapon {
    constructor(player) {
        this.player = player;
        this.name = 'Blob';
        this.level = 1;
        this.damage = 3 + this.level;
        this.speed = 2 + this.level * 0.5;
        this.blob = null;
    }

    update(dt) {
        if (!this.blob || !this.blob.alive) {
            this.blob = new Blob(this.player.x, this.player.y, this.damage, this.speed);
            projectiles.push(this.blob);
        }
        this.blob.update(dt);
    }

    upgrade() {
        if (this.level < 10) {
            this.level++;
            this.damage = 3 + this.level;
            this.speed = 2 + this.level * 0.5;
            if (this.blob) {
                this.blob.damage = this.damage;
                this.blob.speed = this.speed;
            }
        }
    }
}

class HeavyAttack {
    constructor(player) {
        this.player = player;
        this.name = 'Heavy';
        this.level = 1;
        this.damage = 10 + this.level * 5;
        this.cooldown = 5 - this.level * 0.3;
        this.timer = this.cooldown;
        this.numShots = 4 + Math.floor(this.level / 2);
        this.ready = true;
    }

    update(dt) {
        if (!this.ready) {
            this.timer += dt;
            if (this.timer >= this.cooldown) this.ready = true;
        }
        if (this.player.keys[' '] && this.ready) {
            this.fire();
            this.ready = false;
            this.timer = 0;
        }
    }

    fire() {
        const angleStep = 2 * Math.PI / this.numShots;
        for (let i = 0; i < this.numShots; i++) {
            const angle = i * angleStep;
            projectiles.push(new Projectile(this.player.x, this.player.y, Math.cos(angle), Math.sin(angle), this.damage, COLORS.BLUE, true));
        }
    }

    upgrade() {
        if (this.level < 10) {
            this.level++;
            this.damage = 10 + this.level * 5;
            this.cooldown = 5 - this.level * 0.3;
            this.numShots = 4 + Math.floor(this.level / 2);
            this.ready = false;
            this.timer = 0;
        }
    }
}

// Game objects
const player = new Player();
let enemies = [];
let projectiles = [];
let items = [];
let spawnTimer = 0;
const baseSpawnInterval = 3;

// Utility functions
function findNearestEnemy(x, y) {
    let nearest = null;
    let minDist = Infinity;
    enemies.forEach(enemy => {
        const dist = distance(x, y, enemy.x, enemy.y);
        if (dist < minDist) {
            minDist = dist;
            nearest = enemy;
        }
    });
    return nearest;
}

function spawnEnemy() {
    const side = ['top', 'bottom', 'left', 'right'][Math.floor(Math.random() * 4)];
    let x, y;
    if (side === 'top') { x = Math.random() * SCREEN_WIDTH; y = -20; }
    else if (side === 'bottom') { x = Math.random() * SCREEN_WIDTH; y = SCREEN_HEIGHT + 20; }
    else if (side === 'left') { x = -20; y = Math.random() * SCREEN_HEIGHT; }
    else { x = SCREEN_WIDTH + 20; y = Math.random() * SCREEN_HEIGHT; }
    
    let type;
    if (player.level < 10) type = Math.random() < 0.85 ? 'normal' : Math.random() < 0.67 ? 'fast' : 'strong';
    else if (player.level < 20) type = Math.random() < 0.6 ? 'normal' : Math.random() < 0.5 ? 'fast' : 'strong';
    else type = Math.random() < 0.1 ? 'normal' : Math.random() < 0.5 ? 'fast' : 'strong';
    
    enemies.push(new Enemy(x, y, type, player.level));
}

// Event listeners
window.addEventListener('keydown', e => player.keys[e.key] = true);
window.addEventListener('keyup', e => player.keys[e.key] = false);
canvas.addEventListener('click', e => {
    if (gameState === 'upgrading') {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        const allMaxed = player.weapons.every(w => w.level >= 10);
        if (allMaxed && x > 300 && x < 500 && y > 280 && y < 320) {
            player.health = player.maxHealth;
            gameState = 'playing';
        } else {
            for (let i = 0; i < 3; i++) {
                if (x > 210 + i * 200 && x < 390 + i * 200 && y > 280 && y < 360 && player.weapons[i].level < 10) {
                    player.weapons[i].upgrade();
                    gameState = 'playing';
                    break;
                }
            }
        }
    }
});

// Main game loop
let lastTime = performance.now();
function gameLoop() {
    const now = performance.now();
    const dt = Math.min((now - lastTime) / 1000, 0.1);
    lastTime = now;

    ctx.clearRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

    if (gameState === 'playing') {
        // Update
        player.update(dt);
        enemies.forEach(enemy => enemy.update(dt));
        projectiles.forEach(p => p.update(dt));

        spawnTimer += dt;
        const spawnInterval = Math.max(0.5, baseSpawnInterval - 0.5 * (player.level - 1));
        if (spawnTimer >= spawnInterval) {
            spawnEnemy();
            spawnTimer = 0;
        }

        // Collisions
        projectiles.forEach((p, pi) => {
            enemies.forEach((e, ei) => {
                if (distance(p.x, p.y, e.x, e.y) < (p.size + e.size) / 2) {
                    if (!p.hitEnemies.has(e)) {
                        e.health -= p.damage;
                        p.hitEnemies.add(e);
                        if (!p.piercing && !(p instanceof Blob)) projectiles.splice(pi, 1);
                        if (e.health <= 0) {
                            enemies.splice(ei, 1);
                            player.killCount++;
                            if (Math.random() < 0.7) items.push(new ExpItem(e.x, e.y));
                            else if (Math.random() < 0.03 / 0.7) items.push(new HealthItem(e.x, e.y));
                            if ([100, 200, 300, 400].includes(player.killCount)) {
                                const side = ['top', 'bottom', 'left', 'right'][Math.floor(Math.random() * 4)];
                                let x, y;
                                if (side === 'top') { x = Math.random() * SCREEN_WIDTH; y = -50; }
                                else if (side === 'bottom') { x = Math.random() * SCREEN_WIDTH; y = SCREEN_HEIGHT + 50; }
                                else if (side === 'left') { x = -50; y = Math.random() * SCREEN_HEIGHT; }
                                else { x = SCREEN_WIDTH + 50; y = Math.random() * SCREEN_HEIGHT; }
                                enemies.push(new Enemy(x, y, 'boss', player.level));
                            }
                        }
                    }
                }
            });
        });

        items.forEach((item, ii) => {
            if (distance(player.x, player.y, item.x, item.y) < 50) {
                if (item instanceof ExpItem) {
                    player.experience += item.value;
                    if (player.experience >= player.expToNextLevel) {
                        player.level++;
                        player.experience -= player.expToNextLevel;
                        player.expToNextLevel = player.level;
                        gameState = 'upgrading';
                    }
                } else if (item instanceof HealthItem) {
                    player.health = Math.min(player.maxHealth, player.health + item.value);
                }
                items.splice(ii, 1);
            }
        });

        enemies.forEach(e => {
            if (distance(player.x, player.y, e.x, e.y) < (player.size + e.size) / 2) {
                player.health -= e.damageRate * dt;
            }
        });

        if (player.killCount >= 500) {
            gameState = 'end';
            gameResult = 'win';
        } else if (player.health <= 0) {
            gameState = 'end';
            gameResult = 'loss';
        }
    }

    // Draw
    if (gameState === 'playing' || gameState === 'upgrading') {
        player.draw();
        enemies.forEach(e => e.draw());
        projectiles.forEach(p => p.draw());
        items.forEach(i => i.draw());

        // UI
        ctx.fillStyle = COLORS.RED;
        ctx.fillRect(5, 5, 150, 10);
        ctx.fillStyle = COLORS.GREEN;
        ctx.fillRect(5, 5, 150 * (player.health / player.maxHealth), 10);
        ctx.fillStyle = COLORS.WHITE;
        ctx.font = '20px Arial';
        ctx.fillText(`Health: ${Math.max(0, Math.floor(player.health))}`, 160, 15);
        ctx.fillText(`Level: ${player.level}`, 5, 35);
        ctx.fillStyle = COLORS.BLUE;
        ctx.fillRect(5, 45, 150 * (player.experience / player.expToNextLevel), 10);
        ctx.fillStyle = COLORS.WHITE;
        ctx.fillText(`Kills: ${player.killCount}`, SCREEN_WIDTH / 2 - 50, 15);

        player.weapons.forEach((w, i) => {
            ctx.fillStyle = (w.name === 'Heavy' && !w.ready) ? COLORS.RED : COLORS.WHITE;
            ctx.fillText(`[${i+1}] ${w.name} Lvl ${w.level}`, SCREEN_WIDTH - 150, 15 + i * 30);
        });
    }

    if (gameState === 'upgrading') {
        ctx.fillStyle = COLORS.GRAY;
        ctx.fillRect(100, 200, 600, 200);
        ctx.fillStyle = COLORS.WHITE;
        ctx.font = '24px Arial';
        ctx.fillText('Level Up! Choose an upgrade:', 250, 240);
        
        const allMaxed = player.weapons.every(w => w.level >= 10);
        if (allMaxed) {
            ctx.fillStyle = COLORS.LIGHT_GRAY;
            ctx.fillRect(300, 280, 200, 40);
            ctx.fillStyle = COLORS.WHITE;
            ctx.font = '20px Arial';
            ctx.fillText('Restore Health', 340, 305);
        } else {
            player.weapons.forEach((w, i) => {
                ctx.fillStyle = w.level >= 10 ? COLORS.GRAY : COLORS.LIGHT_GRAY;
                ctx.fillRect(210 + i * 200, 280, 180, 80);
                ctx.fillStyle = COLORS.WHITE;
                ctx.font = '20px Arial';
                ctx.fillText(`${w.level < 10 ? i + 1 : 'X'}: ${w.name} Lvl ${w.level}`, 220 + i * 200, 320);
            });
        }
    }

    if (gameState === 'end') {
        ctx.fillStyle = COLORS.GRAY;
        ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
        ctx.fillStyle = COLORS.WHITE;
        ctx.font = '48px Arial';
        ctx.fillText(gameResult === 'win' ? 'You Won!' : 'You Lost!', 300, 250);
        ctx.font = '24px Arial';
        ctx.fillText(`Level: ${player.level} Kills: ${player.killCount}`, 320, 350);
    }

    projectiles = projectiles.filter(p => p.lifetime > 0 && p.isOnScreen());

    requestAnimationFrame(gameLoop);
}

gameLoop();