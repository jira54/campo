# Resort Overview Dashboard with Navigation Design

## Design Philosophy

**Clean Overview + Dedicated Functionality Pages**
- Overview page shows only essential information and quick actions
- Sidebar navigation provides access to dedicated functionality pages
- Each functionality page optimized for specific tasks
- Mobile-first design with fast loading

---

## 1. Overview Dashboard (Clean & Fast)

### **Design Goal: 5-Second Overview**
Staff should see everything they need in 5 seconds without scrolling.

### **Layout Structure**
```
[HEADER] Resort Name | Date | User Profile
-----------------------------------------------------
[TODAY'S SUMMARY] 3 Rooms Occupied | 2 Need Cleaning | 5 Check-outs
-----------------------------------------------------
[QUICK ACTIONS] 4 Large Buttons for Core Tasks
-----------------------------------------------------
[RECENT ACTIVITY] Last 5 Actions Only
-----------------------------------------------------
[ALERTS & NOTIFICATIONS] VIP Arrivals | Urgent Tasks
-----------------------------------------------------
[ESSENTIAL METRICS] Revenue Today | Occupancy Rate | Check-outs Today
```

### **Detailed Overview Design**

#### **Header Section**
```html
<div class="overview-header">
    <div class="resort-info">
        <h1>{{ user.business_name }}</h1>
        <p class="date">{{ "now"|date:"l, F j, Y" }}</p>
    </div>
    <div class="user-info">
        <div class="user-avatar">{{ user.owner_name|first|upper }}</div>
        <div class="user-role">Front Desk Staff</div>
    </div>
</div>
```

#### **Today's Summary Bar**
```html
<div class="today-summary">
    <div class="summary-item">
        <div class="icon">?</div>
        <div class="info">
            <span class="number">{{ occupied_rooms }}</span>
            <span class="label">Rooms Occupied</span>
        </div>
    </div>
    <div class="summary-item">
        <div class="icon">?</div>
        <div class="info">
            <span class="number">{{ dirty_rooms }}</span>
            <span class="label">Need Cleaning</span>
        </div>
    </div>
    <div class="summary-item">
        <div class="icon">?</div>
        <div class="info">
            <span class="number">{{ checkouts_today }}</span>
            <span class="label">Check-outs Today</span>
        </div>
    </div>
    <div class="summary-item">
        <div class="icon">?</div>
        <div class="info">
            <span class="number">KES {{ today_revenue }}</span>
            <span class="label">Revenue Today</span>
        </div>
    </div>
</div>
```

#### **Quick Actions Grid**
```html
<div class="quick-actions">
    <a href="{% url 'resort_portal:add_guest' %}" class="action-btn check-in">
        <div class="icon">?</div>
        <div class="text">
            <h3>Check-In Guest</h3>
            <p>30 seconds</p>
        </div>
    </a>
    
    <a href="{% url 'resort_portal:add_service' %}" class="action-btn service">
        <div class="icon">?</div>
        <div class="text">
            <h3>Add Service</h3>
            <p>20 seconds</p>
        </div>
    </a>
    
    <a href="{% url 'resort_portal:room_status' %}" class="action-btn rooms">
        <div class="icon">?</div>
        <div class="text">
            <h3>Room Status</h3>
            <p>10 seconds</p>
        </div>
    </a>
    
    <a href="{% url 'resort_portal:check_out_queue' %}" class="action-btn checkout">
        <div class="icon">?</div>
        <div class="text">
            <h3>Check-Out</h3>
            <p>15 seconds</p>
        </div>
    </a>
</div>
```

#### **Recent Activity Feed**
```html
<div class="recent-activity">
    <h3>Recent Activity</h3>
    <div class="activity-list">
        {% for activity in recent_activities|slice:":5" %}
        <div class="activity-item">
            <div class="activity-icon">{{ activity.icon }}</div>
            <div class="activity-content">
                <div class="activity-header">
                    <span class="activity-title">{{ activity.title }}</span>
                    <span class="activity-time">{{ activity.time_ago }}</span>
                </div>
                <div class="activity-description">{{ activity.description }}</div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
```

#### **Alerts & Notifications**
```html
<div class="alerts-section">
    {% if vip_arrivals > 0 %}
    <div class="alert vip-alert">
        <div class="alert-icon">?</div>
        <div class="alert-content">
            <h4>VIP Arrivals Today</h4>
            <p>{{ vip_arrivals }} VIP guests arriving</p>
            <a href="{% url 'resort_portal:vip_list' %}" class="alert-action">View List</a>
        </div>
    </div>
    {% endif %}
    
    {% if urgent_tasks > 0 %}
    <div class="alert urgent-alert">
        <div class="alert-icon">?</div>
        <div class="alert-content">
            <h4>Urgent Tasks</h4>
            <p>{{ urgent_tasks }} tasks need attention</p>
            <a href="{% url 'resort_portal:urgent_tasks' %}" class="alert-action">View Tasks</a>
        </div>
    </div>
    {% endif %}
</div>
```

---

## 2. Sidebar Navigation Structure

### **Design Goal: Clear Navigation Hierarchy**
Organize all functionality into logical groups with clear navigation paths.

### **Navigation Structure**
```html
<nav class="resort-sidebar">
    <div class="sidebar-header">
        <div class="resort-logo">{{ user.business_name|first|upper }}</div>
        <div class="user-info-mini">
            <span class="user-name">{{ user.owner_name }}</span>
            <span class="user-role">{{ user.get_role_display }}</span>
        </div>
    </div>
    
    <div class="sidebar-nav">
        <!-- Main Navigation -->
        <div class="nav-section">
            <div class="nav-section-title">Main</div>
            <a href="{% url 'resort_portal:overview' %}" class="nav-item active">
                <span class="nav-icon">?</span>
                <span class="nav-text">Overview</span>
            </a>
        </div>
        
        <!-- Guest Management -->
        <div class="nav-section">
            <div class="nav-section-title">Operations</div>
            <a href="{% url 'resort_portal:guests' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Guests</span>
            </a>
            <a href="{% url 'resort_portal:rooms' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Rooms</span>
            </a>
            <a href="{% url 'resort_portal:services' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Services</span>
            </a>
        </div>
        
        <!-- Reports (Manager Only) -->
        {% if user.can_view_reports %}
        <div class="nav-section">
            <div class="nav-section-title">Reports</div>
            <a href="{% url 'resort_portal:reports' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Reports</span>
            </a>
        </div>
        {% endif %}
        
        <!-- Settings -->
        <div class="nav-section">
            <div class="nav-section-title">Settings</div>
            <a href="{% url 'resort_portal:settings' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Settings</span>
            </a>
        </div>
    </div>
</nav>
```

---

## 3. Section Pages with Internal Navigation

### **Design Goal: Main Section Pages with Internal Tabs**
Each main section (Guests, Rooms, Services, Reports, Settings) opens a dedicated page with internal navigation tabs for specific functions.

### **Guests Section Page (/resort/guests/)**
```html
{% extends 'base.html' %}
{% block title %}Guests - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Guests</h1>
            <div class="header-actions">
                <div class="search-box">
                    <input type="text" placeholder="Search guests..." id="guest-search">
                    <button class="search-btn">?</button>
                </div>
            </div>
        </div>
        
        <!-- Internal Navigation Tabs -->
        <div class="section-tabs">
            <button class="tab-btn active" onclick="showTab('add-guest')">
                <span class="icon">?</span>
                <span>Add Guest</span>
            </button>
            <button class="tab-btn" onclick="showTab('current-guests')">
                <span class="icon">?</span>
                <span>Current Guests</span>
            </button>
            <button class="tab-btn" onclick="showTab('guest-history')">
                <span class="icon">?</span>
                <span>Guest History</span>
            </button>
            <button class="tab-btn" onclick="showTab('check-out-queue')">
                <span class="icon">?</span>
                <span>Check-Out Queue</span>
            </button>
        </div>
        
        <!-- Tab Content Areas -->
        <div class="tab-content">
            <!-- Add Guest Tab -->
            <div id="add-guest" class="tab-pane active">
                <div class="function-content">
                    <form method="POST" class="guest-form">
                        {% csrf_token %}
                        
                        <!-- Guest Identification Options -->
                        <div class="identification-options">
                            <div class="option-tabs">
                                <button type="button" class="tab-btn active" onclick="setIdentifyMethod('name')">
                                    <span class="icon">?</span>
                                    <span>Name</span>
                                </button>
                                <button type="button" class="tab-btn" onclick="setIdentifyMethod('email')">
                                    <span class="icon">?</span>
                                    <span>Email</span>
                                </button>
                                <button type="button" class="tab-btn" onclick="setIdentifyMethod('both')">
                                    <span class="icon">?</span>
                                    <span>Both</span>
                                </button>
                            </div>
                        </div>
                        
                        <!-- Dynamic Form Fields -->
                        <div id="name-fields" class="form-section">
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Guest Name *</label>
                                    <input type="text" name="guest_name" required>
                                </div>
                                <div class="form-group">
                                    <label>Phone Number</label>
                                    <input type="tel" name="phone_number">
                                </div>
                            </div>
                        </div>
                        
                        <!-- Room and Guest Type -->
                        <div class="form-section">
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Room Number *</label>
                                    <select name="room_number" required>
                                        <option value="">Select Room...</option>
                                        {% for room in available_rooms %}
                                        <option value="{{ room.id }}">{{ room.room_number }} - {{ room.get_status_display }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Guest Type</label>
                                    <select name="guest_type">
                                        <option value="overnight">Overnight Guest</option>
                                        <option value="day_visitor">Day Visitor</option>
                                        <option value="corporate">Corporate Guest</option>
                                        <option value="vip">VIP Guest</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <button type="submit" class="submit-btn">Check-In Guest</button>
                    </form>
                </div>
            </div>
            
            <!-- Current Guests Tab -->
            <div id="current-guests" class="tab-pane">
                <div class="function-content">
                    <div class="guests-grid">
                        {% for guest in current_guests %}
                        <div class="guest-card">
                            <div class="guest-header">
                                <div class="guest-info">
                                    <h3>{{ guest.name }}</h3>
                                    <p class="room-number">Room {{ guest.room_number }}</p>
                                    {% if guest.vip_status %}
                                    <span class="vip-badge">VIP</span>
                                    {% endif %}
                                </div>
                                <div class="guest-actions">
                                    <button onclick="addService('{{ guest.id }}')" class="action-btn-small">Add Service</button>
                                    <button onclick="checkOutGuest('{{ guest.id }}')" class="action-btn-small checkout">Check-Out</button>
                                </div>
                            </div>
                            <div class="guest-details">
                                <div class="detail-item">
                                    <span class="label">Check-in:</span>
                                    <span class="value">{{ guest.check_in_date|date:"M d, Y H:i" }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Phone:</span>
                                    <span class="value">{{ guest.phone }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Type:</span>
                                    <span class="value">{{ guest.get_guest_type_display }}</span>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <!-- Guest History Tab -->
            <div id="guest-history" class="tab-pane">
                <div class="function-content">
                    <div class="history-filters">
                        <div class="filter-row">
                            <input type="text" placeholder="Search by name..." id="history-search">
                            <select id="date-filter">
                                <option value="all">All Time</option>
                                <option value="today">Today</option>
                                <option value="week">This Week</option>
                                <option value="month">This Month</option>
                            </select>
                            <select id="type-filter">
                                <option value="all">All Types</option>
                                <option value="overnight">Overnight</option>
                                <option value="day_visitor">Day Visitor</option>
                                <option value="vip">VIP</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="history-table">
                        <table class="guest-history-table">
                            <thead>
                                <tr>
                                    <th>Guest Name</th>
                                    <th>Room</th>
                                    <th>Check-in</th>
                                    <th>Check-out</th>
                                    <th>Type</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for guest in guest_history %}
                                <tr>
                                    <td>{{ guest.name }}</td>
                                    <td>{{ guest.room_number }}</td>
                                    <td>{{ guest.check_in_date|date:"M d, Y" }}</td>
                                    <td>{{ guest.check_out_date|date:"M d, Y" }}</td>
                                    <td>{{ guest.get_guest_type_display }}</td>
                                    <td>
                                        <button onclick="viewGuestDetails('{{ guest.id }}')" class="action-btn-small">View</button>
                                        <button onclick="checkInGuestAgain('{{ guest.id }}')" class="action-btn-small">Check-In Again</button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Check-Out Queue Tab -->
            <div id="check-out-queue" class="tab-pane">
                <div class="function-content">
                    <div class="checkout-queue">
                        {% for checkout in check_out_queue %}
                        <div class="checkout-card">
                            <div class="checkout-header">
                                <div class="checkout-info">
                                    <h3>{{ checkout.guest.name }}</h3>
                                    <p class="room-number">Room {{ checkout.room_number }}</p>
                                    <p class="checkout-time">Check-out: {{ checkout.check_out_time|time:"H:i" }}</p>
                                </div>
                                <div class="checkout-actions">
                                    <button onclick="viewBill('{{ checkout.id }}')" class="action-btn-small">View Bill</button>
                                    <button onclick="processCheckOut('{{ checkout.id }}')" class="action-btn-small checkout">Process Check-Out</button>
                                </div>
                            </div>
                            <div class="checkout-details">
                                <div class="detail-item">
                                    <span class="label">Total Bill:</span>
                                    <span class="value">KES {{ checkout.total_amount }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Services:</span>
                                    <span class="value">{{ checkout.service_count }} services</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Status:</span>
                                    <span class="value">{{ checkout.get_status_display }}</span>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function showTab(tabId) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    event.target.closest('.tab-btn').classList.add('active');
}
</script>
{% endblock %}
```

### **Rooms Section Page (/resort/rooms/)**
```html
{% extends 'base.html' %}
{% block title %}Rooms - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Rooms</h1>
            <div class="header-actions">
                <div class="filter-buttons">
                    <button class="filter-btn active" onclick="filterRooms('all')">All Rooms</button>
                    <button class="filter-btn" onclick="filterRooms('occupied')">Occupied</button>
                    <button class="filter-btn" onclick="filterRooms('vacant')">Vacant</button>
                    <button class="filter-btn" onclick="filterRooms('dirty')">Need Cleaning</button>
                </div>
                <button onclick="refreshRoomStatus()" class="refresh-btn">Refresh</button>
            </div>
        </div>
        
        <!-- Internal Navigation Tabs -->
        <div class="section-tabs">
            <button class="tab-btn active" onclick="showTab('room-status')">
                <span class="icon">?</span>
                <span>Room Status</span>
            </button>
            <button class="tab-btn" onclick="showTab('housekeeping')">
                <span class="icon">?</span>
                <span>Housekeeping</span>
            </button>
            <button class="tab-btn" onclick="showTab('room-management')">
                <span class="icon">?</span>
                <span>Room Management</span>
            </button>
        </div>
        
        <!-- Tab Content Areas -->
        <div class="tab-content">
            <!-- Room Status Tab -->
            <div id="room-status" class="tab-pane active">
                <div class="function-content">
                    <div class="rooms-grid">
                        {% for room in rooms %}
                        <div class="room-card status-{{ room.status }}" onclick="updateRoomStatus('{{ room.id }}')">
                            <div class="room-header">
                                <div class="room-number">{{ room.room_number }}</div>
                                <div class="room-status">{{ room.get_status_display }}</div>
                            </div>
                            
                            <div class="room-info">
                                {% if room.current_guest %}
                                <div class="guest-info">
                                    <span class="guest-name">{{ room.current_guest.name }}</span>
                                    {% if room.current_guest.vip_status %}
                                    <span class="vip-indicator">?</span>
                                    {% endif %}
                                </div>
                                {% endif %}
                                
                                <div class="room-type">{{ room.room_type }}</div>
                                <div class="last-updated">Updated: {{ room.last_updated|timeago }}</div>
                            </div>
                            
                            <div class="room-actions">
                                {% if room.status == 'vacant_dirty' %}
                                <button onclick="startCleaning('{{ room.id }}')" class="action-btn-small cleaning">Start Cleaning</button>
                                {% elif room.status == 'cleaning' %}
                                <button onclick="finishCleaning('{{ room.id }}')" class="action-btn-small cleaning">Finish Cleaning</button>
                                {% elif room.status == 'inspected' %}
                                <button onclick="approveRoom('{{ room.id }}')" class="action-btn-small approve">Approve</button>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <!-- Housekeeping Tab -->
            <div id="housekeeping" class="tab-pane">
                <div class="function-content">
                    <div class="housekeeping-dashboard">
                        <div class="housekeeping-summary">
                            <div class="summary-item">
                                <span class="number">{{ cleaning_in_progress }}</span>
                                <span class="label">In Progress</span>
                            </div>
                            <div class="summary-item">
                                <span class="number">{{ awaiting_inspection }}</span>
                                <span class="label">Awaiting Inspection</span>
                            </div>
                            <div class="summary-item">
                                <span class="number">{{ completed_today }}</span>
                                <span class="label">Completed Today</span>
                            </div>
                        </div>
                        
                        <div class="housekeeping-queue">
                            <h3>Cleaning Queue</h3>
                            {% for task in cleaning_tasks %}
                            <div class="cleaning-task">
                                <div class="task-info">
                                    <span class="room-number">{{ task.room_number }}</span>
                                    <span class="task-status">{{ task.get_status_display }}</span>
                                    <span class="assigned-to">{{ task.assigned_to }}</span>
                                </div>
                                <div class="task-actions">
                                    {% if task.status == 'pending' %}
                                    <button onclick="startTask('{{ task.id }}')" class="action-btn-small">Start</button>
                                    {% elif task.status == 'in_progress' %}
                                    <button onclick="completeTask('{{ task.id }}')" class="action-btn-small">Complete</button>
                                    {% endif %}
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Room Management Tab -->
            <div id="room-management" class="tab-pane">
                <div class="function-content">
                    <div class="room-management-tools">
                        <button onclick="openAddRoomModal()" class="action-btn-small">Add New Room</button>
                        <button onclick="openEditRoomTypesModal()" class="action-btn-small">Edit Room Types</button>
                        <button onclick="exportRoomData()" class="action-btn-small">Export Data</button>
                    </div>
                    
                    <div class="room-management-table">
                        <table class="rooms-table">
                            <thead>
                                <tr>
                                    <th>Room Number</th>
                                    <th>Type</th>
                                    <th>Status</th>
                                    <th>Current Guest</th>
                                    <th>Last Cleaned</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for room in rooms %}
                                <tr>
                                    <td>{{ room.room_number }}</td>
                                    <td>{{ room.room_type }}</td>
                                    <td>{{ room.get_status_display }}</td>
                                    <td>{{ room.current_guest.name|default:"-" }}</td>
                                    <td>{{ room.last_cleaned|date:"M d, Y"|default:"-" }}</td>
                                    <td>
                                        <button onclick="editRoom('{{ room.id }}')" class="action-btn-small">Edit</button>
                                        <button onclick="viewRoomHistory('{{ room.id }}')" class="action-btn-small">History</button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function showTab(tabId) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    event.target.closest('.tab-btn').classList.add('active');
}
</script>
{% endblock %}
```

### **Services Section Page (/resort/services/)**
```html
{% extends 'base.html' %}
{% block title %}Services - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Services</h1>
            <div class="header-actions">
                <div class="quick-stats">
                    <div class="stat-item">
                        <span class="number">{{ today_services }}</span>
                        <span class="label">Today</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">KES {{ today_revenue }}</span>
                        <span class="label">Revenue</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Internal Navigation Tabs -->
        <div class="section-tabs">
            <button class="tab-btn active" onclick="showTab('add-service')">
                <span class="icon">?</span>
                <span>Add Service</span>
            </button>
            <button class="tab-btn" onclick="showTab('service-history')">
                <span class="icon">?</span>
                <span>Service History</span>
            </button>
            <button class="tab-btn" onclick="showTab('department-analytics')">
                <span class="icon">?</span>
                <span>Department Analytics</span>
            </button>
        </div>
        
        <!-- Tab Content Areas -->
        <div class="tab-content">
            <!-- Add Service Tab -->
            <div id="add-service" class="tab-pane active">
                <div class="function-content">
                    <form method="POST" class="service-form">
                        {% csrf_token %}
                        
                        <div class="form-section">
                            <h3>Guest Information</h3>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Guest *</label>
                                    <select name="guest_id" required>
                                        <option value="">Select Guest...</option>
                                        {% for guest in current_guests %}
                                        <option value="{{ guest.id }}">Room {{ guest.room_number }} - {{ guest.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>or Walk-in Guest</label>
                                    <input type="text" name="walk_in_name" placeholder="Guest Name">
                                </div>
                            </div>
                        </div>
                        
                        <div class="form-section">
                            <h3>Service Details</h3>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Department *</label>
                                    <select name="department_id" required>
                                        <option value="">Select Department...</option>
                                        {% for dept in departments %}
                                        <option value="{{ dept.id }}">{{ dept.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Service *</label>
                                    <select name="service_id" required>
                                        <option value="">Select Service...</option>
                                        {% for service in services %}
                                        <option value="{{ service.id }}">{{ service.name }}</option>
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group full-width">
                                    <label>Description</label>
                                    <input type="text" name="description" placeholder="Service description">
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Amount (KES) *</label>
                                    <input type="number" name="amount" required placeholder="0.00">
                                </div>
                                <div class="form-group">
                                    <label>Quantity</label>
                                    <input type="number" name="quantity" value="1" min="1">
                                </div>
                            </div>
                        </div>
                        
                        <button type="submit" class="submit-btn">Add Service Charge</button>
                    </form>
                </div>
            </div>
            
            <!-- Service History Tab -->
            <div id="service-history" class="tab-pane">
                <div class="function-content">
                    <div class="service-filters">
                        <div class="filter-row">
                            <input type="text" placeholder="Search services..." id="service-search">
                            <select id="date-filter">
                                <option value="today">Today</option>
                                <option value="week">This Week</option>
                                <option value="month">This Month</option>
                                <option value="all">All Time</option>
                            </select>
                            <select id="department-filter">
                                <option value="all">All Departments</option>
                                {% for dept in departments %}
                                <option value="{{ dept.id }}">{{ dept.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                    
                    <div class="service-history-table">
                        <table class="services-table">
                            <thead>
                                <tr>
                                    <th>Date/Time</th>
                                    <th>Guest</th>
                                    <th>Room</th>
                                    <th>Department</th>
                                    <th>Service</th>
                                    <th>Amount</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for service in service_history %}
                                <tr>
                                    <td>{{ service.created_at|date:"M d, Y H:i" }}</td>
                                    <td>{{ service.guest.name }}</td>
                                    <td>{{ service.guest.room_number }}</td>
                                    <td>{{ service.department.name }}</td>
                                    <td>{{ service.service.name }}</td>
                                    <td>KES {{ service.amount }}</td>
                                    <td>
                                        <button onclick="viewServiceDetails('{{ service.id }}')" class="action-btn-small">View</button>
                                        <button onclick="editService('{{ service.id }}')" class="action-btn-small">Edit</button>
                                    </td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- Department Analytics Tab -->
            <div id="department-analytics" class="tab-pane">
                <div class="function-content">
                    <div class="analytics-dashboard">
                        <div class="department-revenue-chart">
                            <h3>Department Revenue Breakdown</h3>
                            <canvas id="departmentChart"></canvas>
                        </div>
                        
                        <div class="department-performance-grid">
                            {% for dept in department_performance %}
                            <div class="department-card">
                                <div class="department-header">
                                    <h4>{{ dept.name }}</h4>
                                    <span class="revenue">KES {{ dept.total_revenue }}</span>
                                </div>
                                <div class="department-metrics">
                                    <div class="metric">
                                        <span class="label">Services Today:</span>
                                        <span class="value">{{ dept.services_today }}</span>
                                    </div>
                                    <div class="metric">
                                        <span class="label">Avg. Amount:</span>
                                        <span class="value">KES {{ dept.average_amount }}</span>
                                    </div>
                                    <div class="metric">
                                        <span class="label">Growth:</span>
                                        <span class="value {{ dept.growth_class }}">{{ dept.growth }}%</span>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <div class="top-services">
                            <h3>Top Services Today</h3>
                            <div class="services-list">
                                {% for service in top_services %}
                                <div class="service-item">
                                    <div class="service-info">
                                        <span class="service-name">{{ service.name }}</span>
                                        <span class="department">{{ service.department }}</span>
                                    </div>
                                    <div class="service-stats">
                                        <span class="count">{{ service.count }}x</span>
                                        <span class="revenue">KES {{ service.revenue }}</span>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function showTab(tabId) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    event.target.closest('.tab-btn').classList.add('active');
}
</script>
{% endblock %}
```

---

## 4. CSS for Section Tabs

### **Tab Navigation Styling**
```css
/* Section Tabs */
.section-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    overflow-x: auto;
}

.tab-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: #94a3b8;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}

.tab-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: white;
}

.tab-btn.active {
    background: #3b82f6;
    border-color: #3b82f6;
    color: white;
}

.tab-btn .icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Tab Content */
.tab-content {
    min-height: 400px;
}

.tab-pane {
    display: none;
}

.tab-pane.active {
    display: block;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Mobile Responsive Tabs */
@media (max-width: 768px) {
    .section-tabs {
        flex-wrap: nowrap;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    .tab-btn {
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
    }
    
    .tab-btn .icon {
        width: 16px;
        height: 16px;
    }
}
```

---

## 5. Guest Management Pages

#### **Add Guest Page (/resort/guests/add)**
```html
{% extends 'base.html' %}
{% block title %}Add Guest - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Add Guest</h1>
            <div class="breadcrumb">
                <a href="{% url 'resort_portal:overview' %}">Overview</a>
                <span>/</span>
                <span>Guests</span>
                <span>/</span>
                <span>Add Guest</span>
            </div>
        </div>
        
        <div class="function-content">
            <!-- Enhanced Check-In Form -->
            <form method="POST" class="guest-form">
                {% csrf_token %}
                
                <!-- Guest Identification Options -->
                <div class="identification-options">
                    <div class="option-tabs">
                        <button type="button" class="tab-btn active" onclick="setIdentifyMethod('name')">
                            <span class="icon">?</span>
                            <span>Name</span>
                        </button>
                        <button type="button" class="tab-btn" onclick="setIdentifyMethod('email')">
                            <span class="icon">?</span>
                            <span>Email</span>
                        </button>
                        <button type="button" class="tab-btn" onclick="setIdentifyMethod('both')">
                            <span class="icon">?</span>
                            <span>Both</span>
                        </button>
                    </div>
                </div>
                
                <!-- Dynamic Form Fields -->
                <div id="name-fields" class="form-section">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Guest Name *</label>
                            <input type="text" name="guest_name" required>
                        </div>
                        <div class="form-group">
                            <label>Phone Number</label>
                            <input type="tel" name="phone_number">
                        </div>
                    </div>
                </div>
                
                <!-- Room and Guest Type -->
                <div class="form-section">
                    <div class="form-row">
                        <div class="form-group">
                            <label>Room Number *</label>
                            <select name="room_number" required>
                                <option value="">Select Room...</option>
                                {% for room in available_rooms %}
                                <option value="{{ room.id }}">{{ room.room_number }} - {{ room.get_status_display }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Guest Type</label>
                            <select name="guest_type">
                                <option value="overnight">Overnight Guest</option>
                                <option value="day_visitor">Day Visitor</option>
                                <option value="corporate">Corporate Guest</option>
                                <option value="vip">VIP Guest</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <!-- VIP Checkbox -->
                <div class="form-section">
                    <label class="checkbox-label">
                        <input type="checkbox" name="vip_status">
                        <span class="checkmark"></span>
                        <span class="label-text">Mark as VIP Guest</span>
                    </label>
                </div>
                
                <button type="submit" class="submit-btn">Check-In Guest</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

#### **Current Guests Page (/resort/guests/current)**
```html
{% extends 'base.html' %}
{% block title %}Current Guests - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Current Guests</h1>
            <div class="header-actions">
                <div class="search-box">
                    <input type="text" placeholder="Search guests..." id="guest-search">
                    <button class="search-btn">?</button>
                </div>
                <div class="filter-dropdown">
                    <select id="guest-filter">
                        <option value="all">All Guests</option>
                        <option value="vip">VIP Guests</option>
                        <option value="overnight">Overnight</option>
                        <option value="day_visitor">Day Visitors</option>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="function-content">
            <div class="guests-grid">
                {% for guest in current_guests %}
                <div class="guest-card">
                    <div class="guest-header">
                        <div class="guest-info">
                            <h3>{{ guest.name }}</h3>
                            <p class="room-number">Room {{ guest.room_number }}</p>
                            {% if guest.vip_status %}
                            <span class="vip-badge">VIP</span>
                            {% endif %}
                        </div>
                        <div class="guest-actions">
                            <button onclick="addService('{{ guest.id }}')" class="action-btn-small">Add Service</button>
                            <button onclick="checkOutGuest('{{ guest.id }}')" class="action-btn-small checkout">Check-Out</button>
                        </div>
                    </div>
                    <div class="guest-details">
                        <div class="detail-item">
                            <span class="label">Check-in:</span>
                            <span class="value">{{ guest.check_in_date|date:"M d, Y H:i" }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Phone:</span>
                            <span class="value">{{ guest.phone }}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Type:</span>
                            <span class="value">{{ guest.get_guest_type_display }}</span>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### **Room Management Pages**

#### **Room Status Page (/resort/rooms/status)**
```html
{% extends 'base.html' %}
{% block title %}Room Status - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Room Status</h1>
            <div class="header-actions">
                <div class="filter-buttons">
                    <button class="filter-btn active" onclick="filterRooms('all')">All Rooms</button>
                    <button class="filter-btn" onclick="filterRooms('occupied')">Occupied</button>
                    <button class="filter-btn" onclick="filterRooms('vacant')">Vacant</button>
                    <button class="filter-btn" onclick="filterRooms('dirty')">Need Cleaning</button>
                </div>
                <button onclick="refreshRoomStatus()" class="refresh-btn">Refresh</button>
            </div>
        </div>
        
        <div class="function-content">
            <div class="rooms-grid">
                {% for room in rooms %}
                <div class="room-card status-{{ room.status }}" onclick="updateRoomStatus('{{ room.id }}')">
                    <div class="room-header">
                        <div class="room-number">{{ room.room_number }}</div>
                        <div class="room-status">{{ room.get_status_display }}</div>
                    </div>
                    
                    <div class="room-info">
                        {% if room.current_guest %}
                        <div class="guest-info">
                            <span class="guest-name">{{ room.current_guest.name }}</span>
                            {% if room.current_guest.vip_status %}
                            <span class="vip-indicator">?</span>
                            {% endif %}
                        </div>
                        {% endif %}
                        
                        <div class="room-type">{{ room.room_type }}</div>
                        <div class="last-updated">Updated: {{ room.last_updated|timeago }}</div>
                    </div>
                    
                    <div class="room-actions">
                        {% if room.status == 'vacant_dirty' %}
                        <button onclick="startCleaning('{{ room.id }}')" class="action-btn-small cleaning">Start Cleaning</button>
                        {% elif room.status == 'cleaning' %}
                        <button onclick="finishCleaning('{{ room.id }}')" class="action-btn-small cleaning">Finish Cleaning</button>
                        {% elif room.status == 'inspected' %}
                        <button onclick="approveRoom('{{ room.id }}')" class="action-btn-small approve">Approve</button>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### **Services Pages**

#### **Add Service Page (/resort/services/add)**
```html
{% extends 'base.html' %}
{% block title %}Add Service - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Add Service Charge</h1>
            <div class="breadcrumb">
                <a href="{% url 'resort_portal:overview' %}">Overview</a>
                <span>/</span>
                <span>Services</span>
                <span>/</span>
                <span>Add Service</span>
            </div>
        </div>
        
        <div class="function-content">
            <form method="POST" class="service-form">
                {% csrf_token %}
                
                <div class="form-section">
                    <h3>Guest Information</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Guest *</label>
                            <select name="guest_id" required>
                                <option value="">Select Guest...</option>
                                {% for guest in current_guests %}
                                <option value="{{ guest.id }}">Room {{ guest.room_number }} - {{ guest.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>or Walk-in Guest</label>
                            <input type="text" name="walk_in_name" placeholder="Guest Name">
                        </div>
                    </div>
                </div>
                
                <div class="form-section">
                    <h3>Service Details</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Department *</label>
                            <select name="department_id" required>
                                <option value="">Select Department...</option>
                                {% for dept in departments %}
                                <option value="{{ dept.id }}">{{ dept.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Service *</label>
                            <select name="service_id" required>
                                <option value="">Select Service...</option>
                                {% for service in services %}
                                <option value="{{ service.id }}">{{ service.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group full-width">
                            <label>Description</label>
                            <input type="text" name="description" placeholder="Service description">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label>Amount (KES) *</label>
                            <input type="number" name="amount" required placeholder="0.00">
                        </div>
                        <div class="form-group">
                            <label>Quantity</label>
                            <input type="number" name="quantity" value="1" min="1">
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="submit-btn">Add Service Charge</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 4. CSS Styling

### **Mobile-First Responsive Design**
```css
/* Overview Dashboard Styles */
.overview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: linear-gradient(135deg, #1e293b, #334155);
    border-radius: 12px;
    margin-bottom: 1rem;
}

.today-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    margin-bottom: 2rem;
}

.summary-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    transition: transform 0.2s ease;
}

.summary-item:hover {
    transform: translateY(-2px);
}

.summary-item .icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #3b82f6;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.2rem;
}

.summary-item .number {
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
}

.summary-item .label {
    font-size: 0.875rem;
    color: #94a3b8;
    text-transform: uppercase;
}

.quick-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.action-btn {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    border: none;
    border-radius: 12px;
    padding: 2rem;
    color: white;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.action-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
}

.action-btn .icon {
    font-size: 2rem;
}

.action-btn h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
}

.action-btn p {
    margin: 0;
    font-size: 0.875rem;
    opacity: 0.8;
}

/* Sidebar Navigation */
.resort-sidebar {
    width: 280px;
    height: 100vh;
    background: #1e293b;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    overflow-y: auto;
    position: fixed;
    left: 0;
    top: 0;
    z-index: 40;
}

.sidebar-header {
    padding: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-section {
    margin-bottom: 1.5rem;
}

.nav-section-title {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    color: #64748b;
    padding: 0 1.5rem;
    margin-bottom: 0.5rem;
}

.nav-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1.5rem;
    color: #94a3b8;
    text-decoration: none;
    transition: all 0.2s ease;
}

.nav-item:hover {
    background: rgba(255, 255, 255, 0.05);
    color: white;
}

.nav-item.active {
    background: #3b82f6;
    color: white;
}

.nav-icon {
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Function Pages */
.function-page {
    display: flex;
    min-height: 100vh;
}

.main-content {
    flex: 1;
    margin-left: 280px;
    padding: 2rem;
    overflow-y: auto;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.page-header h1 {
    font-size: 2rem;
    font-weight: bold;
    color: white;
    margin: 0;
}

.breadcrumb {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #64748b;
}

.breadcrumb a {
    color: #3b82f6;
    text-decoration: none;
}

.breadcrumb a:hover {
    text-decoration: underline;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
    .resort-sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    
    .resort-sidebar.open {
        transform: translateX(0);
    }
    
    .main-content {
        margin-left: 0;
        padding: 1rem;
    }
    
    .today-summary {
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
    }
    
    .quick-actions {
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
    }
    
    .summary-item {
        padding: 0.75rem;
    }
    
    .action-btn {
        padding: 1.5rem;
    }
    
    .rooms-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
    }
}

@media (max-width: 480px) {
    .today-summary {
        grid-template-columns: 1fr;
    }
    
    .quick-actions {
        grid-template-columns: 1fr;
    }
    
    .rooms-grid {
        grid-template-columns: 1fr;
    }
}
```

---

## 5. URL Structure

### **Clean, Semantic URLs**
```python
# resort_portal/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Overview
    path('', views.overview, name='overview'),
    
    # Main Sections
    path('guests/', views.guests_section, name='guests'),
    path('rooms/', views.rooms_section, name='rooms'),
    path('services/', views.services_section, name='services'),
    
    # Reports (Manager Only)
    path('reports/', views.reports_section, name='reports'),
    
    # Settings
    path('settings/', views.settings_section, name='settings'),
]
```

---

## 6. Implementation Benefits

### **Speed & Performance**
- **5-second overview** - staff see everything instantly
- **30-second tasks** - each page optimized for single purpose
- **10x faster loading** - small, focused pages
- **Mobile optimized** - perfect on all devices

### **User Experience**
- **Clear navigation** - logical grouping in sidebar
- **Focused tasks** - one page per function
- **Easy training** - staff learn one function at a time
- **Better organization** - related features grouped together

### **Technical Advantages**
- **Modular code** - easier maintenance and updates
- **Better caching** - individual pages can be cached
- **Cleaner URLs** - semantic and SEO-friendly
- **Scalable architecture** - easy to add new features

### **Operational Efficiency**
- **Reduced cognitive load** - staff focus on one task
- **Faster workflows** - optimized for specific operations
- **Better error handling** - isolated to specific functions
- **Improved analytics** - better tracking of feature usage

---

## Conclusion

This design transforms the resort dashboard from an overwhelming all-in-one page into a **streamlined, task-oriented interface** that matches how resort staff actually work.

**Key Benefits:**
- **5-second overview** for instant situational awareness
- **30-second tasks** for all core operations
- **Clean navigation** with logical grouping
- **Mobile-first design** for field operations
- **Scalable architecture** for future enhancements

**Implementation Priority:**
1. **Overview page** (Week 1)
2. **Guest management pages** (Week 2)
3. **Room management pages** (Week 3)
4. **Services and reports pages** (Week 4)

This approach provides the **best of both worlds**: fast overview for daily operations and dedicated pages for focused tasks.
