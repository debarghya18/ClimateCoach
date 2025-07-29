// Climate AI Platform JavaScript

// Global variables
let climateMap;
let temperatureChart;
let currentUser = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize components
    initializeNavigation();
    initializeSearch();
    initializeModals();
    initializeCharts();
    initializeMap();
    initializeActionCards();
    initializeNotifications();
    
    // Load initial data
    loadDashboardData();
    
    console.log('Climate AI Platform initialized successfully');
}

// Navigation functionality
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const mobileToggle = document.getElementById('mobile-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    // Navigation link clicks
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Handle navigation
            const href = this.getAttribute('href');
            navigateToSection(href);
        });
    });
    
    // Mobile menu toggle
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // User profile dropdown
    const userProfile = document.getElementById('user-profile');
    if (userProfile) {
        userProfile.addEventListener('click', function() {
            showUserMenu();
        });
    }
}

// Search functionality
function initializeSearch() {
    const searchBtn = document.getElementById('search-btn');
    const searchOverlay = document.getElementById('search-overlay');
    const searchClose = document.getElementById('search-close');
    const searchInput = document.getElementById('global-search');
    
    // Open search overlay
    searchBtn.addEventListener('click', function() {
        searchOverlay.style.visibility = 'visible';
        searchOverlay.style.opacity = '1';
        searchInput.focus();
    });
    
    // Close search overlay
    searchClose.addEventListener('click', function() {
        searchOverlay.style.visibility = 'hidden';
        searchOverlay.style.opacity = '0';
    });
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && searchOverlay.style.visibility === 'visible') {
            searchOverlay.style.visibility = 'hidden';
            searchOverlay.style.opacity = '0';
        }
    });
    
    // Search input handling
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        if (query.length > 2) {
            performSearch(query);
        }
    });
}

// Modal functionality
function initializeModals() {
    const locationModal = document.getElementById('location-modal');
    const closeLocationModal = document.getElementById('close-location-modal');
    const cancelLocation = document.getElementById('cancel-location');
    const locationForm = document.querySelector('.location-form');
    
    // Close modal handlers
    [closeLocationModal, cancelLocation].forEach(btn => {
        if (btn) {
            btn.addEventListener('click', function() {
                hideModal(locationModal);
            });
        }
    });
    
    // Form submission
    if (locationForm) {
        locationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleLocationSubmission();
        });
    }
    
    // Close modal on overlay click
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-overlay')) {
            hideModal(e.target);
        }
    });
}

// Charts initialization
function initializeCharts() {
    const tempChartCanvas = document.getElementById('temperature-chart');
    
    if (tempChartCanvas) {
        const ctx = tempChartCanvas.getContext('2d');
        
        temperatureChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: generateDateLabels(30),
                datasets: [{
                    label: 'Temperature (°C)',
                    data: generateTemperatureData(30),
                    borderColor: '#4caf50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        display: true,
                        grid: {
                            color: '#f0f0f0'
                        }
                    }
                }
            }
        });
    }
    
    // Time selector for charts
    const timeSelector = document.querySelector('.time-selector');
    if (timeSelector) {
        timeSelector.addEventListener('change', function() {
            updateChartData(this.value);
        });
    }
}

// Map initialization
function initializeMap() {
    const mapContainer = document.getElementById('climate-map');
    
    if (mapContainer) {
        // Initialize Leaflet map
        climateMap = L.map('climate-map').setView([25.7617, -80.1918], 10);
        
        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(climateMap);
        
        // Add climate risk markers
        addClimateRiskMarkers();
        
        // Map event handlers
        climateMap.on('click', function(e) {
            handleMapClick(e);
        });
    }
}

// Action cards functionality
function initializeActionCards() {
    const actionCards = document.querySelectorAll('.action-card');
    
    actionCards.forEach(card => {
        card.addEventListener('click', function() {
            const action = this.dataset.action;
            handleActionCardClick(action);
        });
    });
    
    // Hero action buttons
    const startAnalysisBtn = document.getElementById('start-analysis');
    const viewDemoBtn = document.getElementById('view-demo');
    
    if (startAnalysisBtn) {
        startAnalysisBtn.addEventListener('click', function() {
            showModal(document.getElementById('location-modal'));
        });
    }
    
    if (viewDemoBtn) {
        viewDemoBtn.addEventListener('click', function() {
            showDemo();
        });
    }
}

// Notifications
function initializeNotifications() {
    const notificationsBtn = document.getElementById('notifications-btn');
    
    if (notificationsBtn) {
        notificationsBtn.addEventListener('click', function() {
            showNotifications();
        });
    }
    
    // Check for new notifications periodically
    setInterval(checkForNotifications, 30000); // Every 30 seconds
}

// Helper functions
function navigateToSection(sectionId) {
    console.log('Navigating to:', sectionId);
    // Implement smooth scrolling or view switching
}

function performSearch(query) {
    console.log('Searching for:', query);
    // Implement search functionality
    // This would typically make an API call to search locations, analyses, etc.
}

function showModal(modal) {
    modal.style.visibility = 'visible';
    modal.style.opacity = '1';
}

function hideModal(modal) {
    modal.style.visibility = 'hidden';
    modal.style.opacity = '0';
}

function handleLocationSubmission() {
    const formData = {
        name: document.getElementById('location-name').value,
        address: document.getElementById('location-address').value,
        latitude: parseFloat(document.getElementById('latitude').value),
        longitude: parseFloat(document.getElementById('longitude').value),
        propertyType: document.getElementById('property-type').value
    };
    
    // Validate form data
    if (!formData.name || !formData.latitude || !formData.longitude) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    // Submit to API
    submitLocationData(formData);
}

function submitLocationData(data) {
    // Show loading state
    showToast('Adding location...', 'info');
    
    // Simulate API call
    setTimeout(() => {
        showToast('Location added successfully!', 'success');
        hideModal(document.getElementById('location-modal'));
        
        // Reset form
        document.querySelector('.location-form').reset();
        
        // Refresh dashboard
        loadDashboardData();
    }, 1500);
}

function generateDateLabels(days) {
    const labels = [];
    const now = new Date();
    
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(now);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    
    return labels;
}

function generateTemperatureData(days) {
    const data = [];
    const baseTemp = 24.5;
    
    for (let i = 0; i < days; i++) {
        const variation = (Math.random() - 0.5) * 8;
        data.push(baseTemp + variation);
    }
    
    return data;
}

function updateChartData(timeRange) {
    let days;
    
    switch(timeRange) {
        case '7d':
            days = 7;
            break;
        case '30d':
            days = 30;
            break;
        case '90d':
            days = 90;
            break;
        case '1y':
            days = 365;
            break;
        default:
            days = 30;
    }
    
    if (temperatureChart) {
        temperatureChart.data.labels = generateDateLabels(days);
        temperatureChart.data.datasets[0].data = generateTemperatureData(days);
        temperatureChart.update();
    }
}

function addClimateRiskMarkers() {
    const riskLocations = [
        { lat: 25.7617, lng: -80.1918, risk: 'high', name: 'Miami Beach' },
        { lat: 25.7907, lng: -80.1300, risk: 'medium', name: 'Downtown Miami' },
        { lat: 25.7257, lng: -80.2374, risk: 'low', name: 'Coral Gables' }
    ];
    
    riskLocations.forEach(location => {
        const color = location.risk === 'high' ? '#ff5722' : 
                     location.risk === 'medium' ? '#ffc107' : '#4caf50';
        
        const marker = L.circleMarker([location.lat, location.lng], {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            fillOpacity: 0.8
        }).addTo(climateMap);
        
        marker.bindPopup(`<b>${location.name}</b><br>Risk Level: ${location.risk.toUpperCase()}`);
    });
}

function handleMapClick(e) {
    console.log('Map clicked at:', e.latlng);
    // Implement map click handling
}

function handleActionCardClick(action) {
    switch(action) {
        case 'location':
            showModal(document.getElementById('location-modal'));
            break;
        case 'analysis':
            startAnalysis();
            break;
        case 'report':
            generateReport();
            break;
        case 'emergency':
            createEmergencyPlan();
            break;
        default:
            console.log('Unknown action:', action);
    }
}

function startAnalysis() {
    showToast('Starting climate analysis...', 'info');
    
    // Simulate analysis process
    setTimeout(() => {
        showToast('Analysis completed!', 'success');
        // Redirect to analysis results
    }, 3000);
}

function generateReport() {
    showToast('Generating climate report...', 'info');
    
    // Simulate report generation
    setTimeout(() => {
        showToast('Report generated successfully!', 'success');
        // Download or display report
    }, 2000);
}

function createEmergencyPlan() {
    showToast('Creating emergency plan...', 'info');
    
    // Simulate emergency plan creation
    setTimeout(() => {
        showToast('Emergency plan created!', 'success');
        // Display emergency plan
    }, 2500);
}

function showDemo() {
    showToast('Loading demo...', 'info');
    
    // Simulate demo loading
    setTimeout(() => {
        showToast('Demo ready!', 'success');
        // Start demo tour
    }, 1500);
}

function showUserMenu() {
    // Implement user profile menu
    console.log('Showing user menu');
}

function showNotifications() {
    // Implement notifications panel
    console.log('Showing notifications');
}

function checkForNotifications() {
    // Check for new notifications from server
    // This would typically make an API call
    console.log('Checking for notifications...');
}

function loadDashboardData() {
    // Load initial dashboard data
    console.log('Loading dashboard data...');
    
    // Simulate data loading
    setTimeout(() => {
        animateStatNumbers();
        console.log('Dashboard data loaded');
    }, 1000);
}

function animateStatNumbers() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const finalValue = stat.textContent;
        const numericValue = parseFloat(finalValue);
        
        if (!isNaN(numericValue)) {
            animateNumber(stat, 0, numericValue, 2000);
        }
    });
}

function animateNumber(element, start, end, duration) {
    const startTime = Date.now();
    const range = end - start;
    
    function update() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = start + (range * progress);
        element.textContent = current.toFixed(1);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = end.toString();
        }
    }
    
    update();
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = type === 'success' ? 'check-circle' : 
                type === 'error' ? 'exclamation-triangle' : 'info-circle';
    
    toast.innerHTML = `
        <i class="fas fa-${icon}"></i>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

// API Communication
class ClimateAPI {
    constructor() {
        this.baseURL = '/api/v1';
        this.token = localStorage.getItem('auth_token');
    }
    
    async request(endpoint, options = {}) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(this.token && { 'Authorization': `Bearer ${this.token}` })
            },
            ...options
        };
        
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            showToast('API request failed', 'error');
            throw error;
        }
    }
    
    async getClimateData(location) {
        return this.request(`/climate/data?lat=${location.lat}&lng=${location.lng}`);
    }
    
    async startAnalysis(locationData) {
        return this.request('/analyze', {
            method: 'POST',
            body: JSON.stringify(locationData)
        });
    }
    
    async getRecommendations(analysisId) {
        return this.request(`/recommendations/${analysisId}`);
    }
}

// Initialize API client
const api = new ClimateAPI();

// Export for use in other modules
window.ClimateApp = {
    api,
    showToast,
    showModal,
    hideModal
};
