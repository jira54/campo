# Resort Dashboard Transition Guide

## Overview

**Step-by-Step Migration from Current Dashboard to New Modular Design**

This guide provides a comprehensive roadmap for transitioning from the current all-in-one resort dashboard to the new modular, section-based design with complete resort operations coverage.

---

## 1. Pre-Transition Preparation

### **1.1 System Assessment**
```bash
# Check current system state
python manage.py check --deploy
python manage.py showmigrations resort_portal
python manage.py collectstatic --dry-run

# Backup current system
python manage.py dumpdata resort_portal > resort_backup_$(date +%Y%m%d).json
cp -r templates/resort_portal templates/resort_portal_backup_$(date +%Y%m%d)
```

### **1.2 Database Analysis**
```sql
-- Check current data structure
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'resort_portal';

-- Analyze current dashboard usage
SELECT COUNT(*) as dashboard_views, 
       DATE(created_at) as view_date,
       user_role
FROM user_activity_log 
WHERE action = 'dashboard_view'
GROUP BY DATE(created_at), user_role
ORDER BY view_date DESC;
```

### **1.3 Performance Baseline**
```python
# Current dashboard performance metrics
import time
from django.test import Client

def benchmark_current_dashboard():
    client = Client()
    start_time = time.time()
    response = client.get('/resort/dashboard/')
    load_time = time.time() - start_time
    
    return {
        'load_time': load_time,
        'response_size': len(response.content),
        'template_size': len(response.content.decode('utf-8')),
        'queries': len(response.context['queries']) if 'queries' in response.context else 0
    }

# Run benchmark 10 times
metrics = [benchmark_current_dashboard() for _ in range(10)]
avg_load_time = sum(m['load_time'] for m in metrics) / len(metrics)
print(f"Current dashboard average load time: {avg_load_time:.2f}s")
```

### **1.4 User Training Assessment**
```python
# Survey current user workflows
from django.contrib.auth.models import User
from resort_portal.models import UserActivity

def analyze_user_workflows():
    workflows = {}
    for user in User.objects.filter(is_active=True):
        activities = UserActivity.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('created_at')
        
        workflow_patterns = []
        for activity in activities:
            workflow_patterns.append({
                'action': activity.action,
                'time': activity.created_at,
                'duration': activity.duration
            })
        
        workflows[user.username] = workflow_patterns
    
    return workflows
```

---

## 2. Phase 1: Infrastructure Setup (Week 1)

### **2.1 Create New URL Structure**
```python
# resort_portal/urls.py - New structure
from django.urls import path
from . import views

urlpatterns = [
    # Overview
    path('', views.overview, name='overview'),
    
    # Guest Operations
    path('guests/', views.guests_section, name='guests'),
    path('rooms/', views.rooms_section, name='rooms'),
    
    # Customer Operations
    path('restaurant/', views.restaurant_section, name='restaurant'),
    path('bar/', views.bar_section, name='bar'),
    path('events/', views.events_section, name='events'),
    path('day-visitors/', views.day_visitors_section, name='day_visitors'),
    
    # Services
    path('services/', views.services_section, name='services'),
    
    # Reports
    path('reports/', views.reports_section, name='reports'),
    
    # Settings
    path('settings/', views.settings_section, name='settings'),
    
    # Legacy redirect (temporary)
    path('dashboard/', views.legacy_dashboard_redirect, name='legacy_dashboard'),
]
```

### **2.2 Create Base Templates**
```html
<!-- templates/resort_portal/base_section.html -->
{% extends 'base.html' %}
{% block title %}{% block section_title %}Resort Portal{% endblock %} - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>{% block page_title %}Section{% endblock %}</h1>
            {% block header_actions %}{% endblock %}
        </div>
        
        <!-- Internal Navigation Tabs -->
        <div class="section-tabs">
            {% block section_tabs %}{% endblock %}
        </div>
        
        <!-- Tab Content Areas -->
        <div class="tab-content">
            {% block tab_content %}{% endblock %}
        </div>
    </div>
</div>

{% block section_scripts %}
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
{% endblock %}
```

### **2.3 Update Sidebar Template**
```html
<!-- templates/resort_portal/sidebar_resort.html -->
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
            <a href="{% url 'resort_portal:overview' %}" class="nav-item {% if request.resolver_match.url_name == 'overview' %}active{% endif %}">
                <span class="nav-icon">?</span>
                <span class="nav-text">Overview</span>
            </a>
        </div>
        
        <!-- Guest Operations -->
        <div class="nav-section">
            <div class="nav-section-title">Guest Operations</div>
            <a href="{% url 'resort_portal:guests' %}" class="nav-item {% if request.resolver_match.url_name == 'guests' %}active{% endif %}">
                <span class="nav-icon">?</span>
                <span class="nav-text">Room Guests</span>
            </a>
            <a href="{% url 'resort_portal:rooms' %}" class="nav-item {% if request.resolver_match.url_name == 'rooms' %}active{% endif %}">
                <span class="nav-icon">?</span>
                <span class="nav-text">Rooms</span>
            </a>
        </div>
        
        <!-- Customer Operations -->
        <div class="nav-section">
            <div class="nav-section-title">Customer Operations</div>
            <a href="{% url 'resort_portal:restaurant' %}" class="nav-item {% if request.resolver_match.url_name == 'restaurant' %}active{% endif %}">
                <span class="nav-icon">?</span>
                <span class="nav-text">Restaurant</span>
            </a>
            <a href="{% url 'resort_portal:bar' %}" class="nav-item {% if request.resolver_match.url_name == 'bar' %}active{% endif %}">
                <span class="nav-icon">?</span>
                <span class="nav-text">Bar</span>
            </a>
            <a href="{% url 'resort_portal:events' %}" class="nav-item {% if request.resolver_match.url_name == 'events' %}active{% endif %}">
                <span class="nav-icon">?</span>
                <span class="nav-text">Events & Spaces</span>
            </a>
            <a href="{% url 'resort_portal:day_visitors' %}" class="nav-item {% if request.resolver_match.url_name == 'day_visitors' %}active{% endif %}">
                <span class="nav-icon">?</span>
                <span class="nav-text">Day Visitors</span>
            </a>
        </div>
        
        <!-- Services -->
        <div class="nav-section">
            <div class="nav-section-title">Services</div>
            <a href="{% url 'resort_portal:services' %}" class="nav-item {% if request.resolver_match.url_name == 'services' %}active{% endif %}">
                <span class="nav-icon">?</span>
                <span class="nav-text">All Services</span>
            </a>
        </div>
        
        <!-- Reports (Manager Only) -->
        {% if user.can_view_reports %}
        <div class="nav-section">
            <div class="nav-section-title">Reports</div>
            <a href="{% url 'resort_portal:reports' %}" class="nav-item {% if request.resolver_match.url_name == 'reports' %}active{% endif %}">
                <span class="nav-icon">?</span>
                <span class="nav-text">Reports</span>
            </a>
        </div>
        {% endif %}
        
        <!-- Settings -->
        <div class="nav-section">
            <div class="nav-section-title">Settings</div>
            <a href="{% url 'resort_portal:settings' %}" class="nav-item {% if request.resolver_match.url_name == 'settings' %}active{% endif %}">
                <span class="nav-icon">?</span>
                <span class="nav-text">Settings</span>
            </a>
        </div>
    </div>
</nav>
```

### **2.4 Add CSS for New Layout**
```css
/* static/css/resort_portal.css */
.function-page {
    display: flex;
    min-height: 100vh;
}

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

/* Mobile Responsive */
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
    
    .section-tabs {
        flex-wrap: nowrap;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }
    
    .tab-btn {
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
    }
}
```

---

## 3. Phase 2: Overview Dashboard (Week 1-2)

### **3.1 Create New Overview Template**
```html
<!-- templates/resort_portal/overview.html -->
{% extends 'base.html' %}
{% block title %}Overview - CampoPawa{% endblock %}

{% block content %}
<div class="overview-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Resort Overview</h1>
            <div class="header-actions">
                <div class="date-display">{{ "now"|date:"l, F j, Y" }}</div>
                <button onclick="refreshOverview()" class="refresh-btn">Refresh</button>
            </div>
        </div>
        
        <!-- Today's Summary Bar -->
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
                    <span class="number">{{ active_restaurant_tables }}</span>
                    <span class="label">Restaurant Tables</span>
                </div>
            </div>
            <div class="summary-item">
                <div class="icon">?</div>
                <div class="info">
                    <span class="number">{{ active_bar_customers }}</span>
                    <span class="label">Bar Customers</span>
                </div>
            </div>
            <div class="summary-item">
                <div class="icon">?</div>
                <div class="info">
                    <span class="number">{{ active_events }}</span>
                    <span class="label">Active Events</span>
                </div>
            </div>
            <div class="summary-item">
                <div class="icon">?</div>
                <div class="info">
                    <span class="number">{{ day_visitors }}</span>
                    <span class="label">Day Visitors</span>
                </div>
            </div>
            <div class="summary-item">
                <div class="icon">?</div>
                <div class="info">
                    <span class="number">KES {{ total_revenue }}</span>
                    <span class="label">Total Revenue</span>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions Grid -->
        <div class="quick-actions">
            <a href="{% url 'resort_portal:guests' %}" class="action-btn check-in">
                <div class="icon">?</div>
                <div class="text">
                    <h3>Guest Check-In</h3>
                    <p>30 seconds</p>
                </div>
            </a>
            
            <a href="{% url 'resort_portal:restaurant' %}" class="action-btn restaurant">
                <div class="icon">?</div>
                <div class="text">
                    <h3>Restaurant</h3>
                    <p>Table management</p>
                </div>
            </a>
            
            <a href="{% url 'resort_portal:bar' %}" class="action-btn bar">
                <div class="icon">?</div>
                <div class="text">
                    <h3>Bar</h3>
                    <p>Tabs & drinks</p>
                </div>
            </a>
            
            <a href="{% url 'resort_portal:events' %}" class="action-btn events">
                <div class="icon">?</div>
                <div class="text">
                    <h3>Events & Spaces</h3>
                    <p>Bookings</p>
                </div>
            </a>
            
            <a href="{% url 'resort_portal:day_visitors' %}" class="action-btn day-visitors">
                <div class="icon">?</div>
                <div class="text">
                    <h3>Day Visitors</h3>
                    <p>Check-in</p>
                </div>
            </a>
            
            <a href="{% url 'resort_portal:rooms' %}" class="action-btn rooms">
                <div class="icon">?</div>
                <div class="text">
                    <h3>Room Status</h3>
                    <p>Housekeeping</p>
                </div>
            </a>
        </div>
        
        <!-- Recent Activity Feed -->
        <div class="recent-activity">
            <h3>Recent Activity</h3>
            <div class="activity-list">
                {% for activity in recent_activities|slice:":8" %}
                <div class="activity-item">
                    <div class="activity-icon">{{ activity.icon }}</div>
                    <div class="activity-content">
                        <div class="activity-header">
                            <span class="activity-title">{{ activity.title }}</span>
                            <span class="activity-time">{{ activity.time_ago }}</span>
                        </div>
                        <div class="activity-description">{{ activity.description }}</div>
                        <div class="activity-category">{{ activity.get_category_display }}</div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Alerts & Notifications -->
        <div class="alerts-section">
            {% if vip_arrivals > 0 %}
            <div class="alert vip-alert">
                <div class="alert-icon">?</div>
                <div class="alert-content">
                    <h4>VIP Arrivals Today</h4>
                    <p>{{ vip_arrivals }} VIP guests arriving</p>
                    <a href="{% url 'resort_portal:guests' %}" class="alert-action">View List</a>
                </div>
            </div>
            {% endif %}
            
            {% if restaurant_queue > 0 %}
            <div class="alert restaurant-alert">
                <div class="alert-icon">?</div>
                <div class="alert-content">
                    <h4>Restaurant Queue</h4>
                    <p>{{ restaurant_queue }} parties waiting for tables</p>
                    <a href="{% url 'resort_portal:restaurant' %}" class="alert-action">Manage Queue</a>
                </div>
            </div>
            {% endif %}
            
            {% if upcoming_events > 0 %}
            <div class="alert events-alert">
                <div class="alert-icon">?</div>
                <div class="alert-content">
                    <h4>Upcoming Events</h4>
                    <p>{{ upcoming_events }} events starting today</p>
                    <a href="{% url 'resort_portal:events' %}" class="alert-action">View Events</a>
                </div>
            </div>
            {% endif %}
        </div>
    </div>
</div>

<script>
function refreshOverview() {
    location.reload();
}
</script>
{% endblock %}
```

### **3.2 Create Overview View**
```python
# resort_portal/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

@login_required
def overview(request):
    # Get today's date
    today = timezone.now().date()
    
    # Room statistics
    occupied_rooms = Room.objects.filter(status='occupied').count()
    
    # Restaurant statistics
    active_restaurant_tables = RestaurantTable.objects.filter(status='occupied').count()
    
    # Bar statistics
    active_bar_customers = BarSeat.objects.filter(status='occupied').count()
    
    # Events statistics
    active_events = Event.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        status='active'
    ).count()
    
    # Day visitors statistics
    day_visitors = DayVisitor.objects.filter(
        check_in_date=today,
        status='active'
    ).count()
    
    # Revenue statistics
    total_revenue = calculate_total_revenue(today)
    
    # Recent activities
    recent_activities = get_recent_activities(limit=8)
    
    # Alerts
    vip_arrivals = Guest.objects.filter(
        check_in_date=today,
        vip_status=True,
        status='checked_in'
    ).count()
    
    restaurant_queue = WalkInQueue.objects.filter(
        date=today,
        status='waiting'
    ).count()
    
    upcoming_events = Event.objects.filter(
        start_date=today,
        status='confirmed'
    ).count()
    
    context = {
        'occupied_rooms': occupied_rooms,
        'active_restaurant_tables': active_restaurant_tables,
        'active_bar_customers': active_bar_customers,
        'active_events': active_events,
        'day_visitors': day_visitors,
        'total_revenue': total_revenue,
        'recent_activities': recent_activities,
        'vip_arrivals': vip_arrivals,
        'restaurant_queue': restaurant_queue,
        'upcoming_events': upcoming_events,
    }
    
    return render(request, 'resort_portal/overview.html', context)

def calculate_total_revenue(date):
    """Calculate total revenue from all sources for given date"""
    from django.db.models import Sum
    
    # Room revenue
    room_revenue = Folio.objects.filter(
        check_out_date=date,
        status='paid'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Restaurant revenue
    restaurant_revenue = RestaurantOrder.objects.filter(
        created_at__date=date,
        status='paid'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Bar revenue
    bar_revenue = BarTab.objects.filter(
        closed_at__date=date,
        status='paid'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Event revenue
    event_revenue = EventBooking.objects.filter(
        start_date=date,
        status='paid'
    ).aggregate(total=Sum('total_cost'))['total'] or 0
    
    # Day visitor revenue
    day_visitor_revenue = DayVisitorPass.objects.filter(
        purchase_date=date
    ).aggregate(total=Sum('price'))['total'] or 0
    
    return room_revenue + restaurant_revenue + bar_revenue + event_revenue + day_visitor_revenue

def get_recent_activities(limit=8):
    """Get recent activities across all departments"""
    from resort_portal.models import UserActivity
    
    return UserActivity.objects.select_related('user').order_by('-created_at')[:limit]
```

---

## 4. Phase 3: Guest Operations (Week 2-3)

### **4.1 Create Guests Section**
```python
# resort_portal/views.py
@login_required
def guests_section(request):
    """Main guests section page"""
    tab = request.GET.get('tab', 'add-guest')
    
    context = {
        'current_tab': tab,
        'available_rooms': Room.objects.filter(status='vacant_clean'),
        'current_guests': Guest.objects.filter(status='checked_in'),
        'guest_history': Guest.objects.filter(status='checked_out').order_by('-check_out_date')[:50],
        'check_out_queue': Folio.objects.filter(
            check_out_date__date=timezone.now().date(),
            status='pending'
        ),
    }
    
    return render(request, 'resort_portal/guests_section.html', context)
```

### **4.2 Create Guests Section Template**
```html
<!-- templates/resort_portal/guests_section.html -->
{% extends 'resort_portal/base_section.html' %}
{% block section_title %}Guests{% endblock %}
{% block page_title %}Guests{% endblock %}

{% block section_tabs %}
<button class="tab-btn {% if current_tab == 'add-guest' %}active{% endif %}" onclick="showTab('add-guest')">
    <span class="icon">?</span>
    <span>Add Guest</span>
</button>
<button class="tab-btn {% if current_tab == 'current-guests' %}active{% endif %}" onclick="showTab('current-guests')">
    <span class="icon">?</span>
    <span>Current Guests</span>
</button>
<button class="tab-btn {% if current_tab == 'guest-history' %}active{% endif %}" onclick="showTab('guest-history')">
    <span class="icon">?</span>
    <span>Guest History</span>
</button>
<button class="tab-btn {% if current_tab == 'check-out-queue' %}active{% endif %}" onclick="showTab('check-out-queue')">
    <span class="icon">?</span>
    <span>Check-Out Queue</span>
</button>
{% endblock %}

{% block tab_content %}
<!-- Add Guest Tab -->
<div id="add-guest" class="tab-pane {% if current_tab == 'add-guest' %}active{% endif %}">
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
<div id="current-guests" class="tab-pane {% if current_tab == 'current-guests' %}active{% endif %}">
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
<div id="guest-history" class="tab-pane {% if current_tab == 'guest-history' %}active{% endif %}">
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
<div id="check-out-queue" class="tab-pane {% if current_tab == 'check-out-queue' %}active{% endif %}">
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
{% endblock %}
```

---

## 5. Phase 4: Customer Operations (Week 3-4)

### **5.1 Create Restaurant Section**
```python
# resort_portal/views.py
@login_required
def restaurant_section(request):
    """Main restaurant section page"""
    tab = request.GET.get('tab', 'table-management')
    
    context = {
        'current_tab': tab,
        'restaurant_tables': RestaurantTable.objects.all(),
        'walk_in_queue': WalkInQueue.objects.filter(status='waiting'),
        'reservations': RestaurantReservation.objects.filter(
            date__gte=timezone.now().date()
        ).order_by('date', 'time'),
        'orders': RestaurantOrder.objects.filter(
            created_at__date=timezone.now().date()
        ).order_by('-created_at'),
    }
    
    return render(request, 'resort_portal/restaurant_section.html', context)
```

### **5.2 Create Bar Section**
```python
@login_required
def bar_section(request):
    """Main bar section page"""
    tab = request.GET.get('tab', 'bar-seating')
    
    context = {
        'current_tab': tab,
        'bar_seats': BarSeat.objects.all(),
        'drink_orders': DrinkOrder.objects.filter(
            created_at__date=timezone.now().date()
        ).order_by('-created_at'),
        'active_tabs': BarTab.objects.filter(status='open'),
        'inventory': BarInventory.objects.all(),
    }
    
    return render(request, 'resort_portal/bar_section.html', context)
```

### **5.3 Create Events Section**
```python
@login_required
def events_section(request):
    """Main events section page"""
    tab = request.GET.get('tab', 'space-availability')
    
    context = {
        'current_tab': tab,
        'event_spaces': EventSpace.objects.all(),
        'bookings': EventBooking.objects.filter(
            start_date__gte=timezone.now().date()
        ).order_by('start_date'),
        'active_events': Event.objects.filter(status='active'),
    }
    
    return render(request, 'resort_portal/events_section.html', context)
```

### **5.4 Create Day Visitors Section**
```python
@login_required
def day_visitors_section(request):
    """Main day visitors section page"""
    tab = request.GET.get('tab', 'visitor-check-in')
    
    context = {
        'current_tab': tab,
        'active_visitors': DayVisitor.objects.filter(status='active'),
        'day_passes': DayVisitorPass.objects.filter(is_active=True),
        'facilities': Facility.objects.all(),
    }
    
    return render(request, 'resort_portal/day_visitors_section.html', context)
```

---

## 6. Phase 5: Data Migration (Week 4)

### **6.1 Create Migration Scripts**
```python
# resort_portal/migrations/0020_migrate_to_new_structure.py
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('resort_portal', '0019_add_new_models'),
    ]

    operations = [
        # Create new models for restaurant operations
        migrations.CreateModel(
            name='RestaurantTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_number', models.CharField(max_length=10)),
                ('capacity', models.IntegerField()),
                ('table_type', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        
        # Create new models for bar operations
        migrations.CreateModel(
            name='BarSeat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat_number', models.CharField(max_length=10)),
                ('seat_type', models.CharField(max_length=20)),
                ('status', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        
        # Create new models for event operations
        migrations.CreateModel(
            name='EventSpace',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('capacity', models.IntegerField()),
                ('space_type', models.CharField(max_length=20)),
                ('rate_per_hour', models.DecimalField(max_digits=10, decimal_places=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        
        # Create new models for day visitor operations
        migrations.CreateModel(
            name='DayVisitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('visit_type', models.CharField(max_length=20)),
                ('number_of_guests', models.IntegerField()),
                ('check_in_time', models.DateTimeField()),
                ('check_out_time', models.DateTimeField(null=True)),
                ('status', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
```

### **6.2 Data Migration Script**
```python
# resort_portal/management/commands/migrate_resort_data.py
from django.core.management.base import BaseCommand
from django.db import transaction
from resort_portal.models import *

class Command(BaseCommand):
    help = 'Migrate resort data to new structure'
    
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Starting resort data migration...')
        
        # Migrate room data
        self.migrate_room_data()
        
        # Migrate service data
        self.migrate_service_data()
        
        # Migrate user activity data
        self.migrate_activity_data()
        
        self.stdout.write('Resort data migration completed successfully!')
    
    def migrate_room_data(self):
        """Migrate existing room data to new structure"""
        self.stdout.write('Migrating room data...')
        
        # Create default restaurant tables
        default_tables = [
            {'table_number': 'T1', 'capacity': 4, 'table_type': 'standard'},
            {'table_number': 'T2', 'capacity': 4, 'table_type': 'standard'},
            {'table_number': 'T3', 'capacity': 6, 'table_type': 'booth'},
            {'table_number': 'T4', 'capacity': 8, 'table_type': 'large'},
        ]
        
        for table_data in default_tables:
            RestaurantTable.objects.get_or_create(
                table_number=table_data['table_number'],
                defaults=table_data
            )
        
        # Create default bar seats
        default_seats = [
            {'seat_number': 'B1', 'seat_type': 'bar_stool'},
            {'seat_number': 'B2', 'seat_type': 'bar_stool'},
            {'seat_number': 'B3', 'seat_type': 'bar_stool'},
            {'seat_number': 'H1', 'seat_type': 'high_top'},
            {'seat_number': 'H2', 'seat_type': 'high_top'},
        ]
        
        for seat_data in default_seats:
            BarSeat.objects.get_or_create(
                seat_number=seat_data['seat_number'],
                defaults=seat_data
            )
        
        self.stdout.write('Room data migration completed.')
    
    def migrate_service_data(self):
        """Migrate existing service data to new structure"""
        self.stdout.write('Migrating service data...')
        
        # Create default event spaces
        default_spaces = [
            {'name': 'Conference Room A', 'capacity': 50, 'space_type': 'conference', 'rate_per_hour': 5000},
            {'name': 'Conference Room B', 'capacity': 30, 'space_type': 'conference', 'rate_per_hour': 3000},
            {'name': 'Ballroom', 'capacity': 200, 'space_type': 'ballroom', 'rate_per_hour': 15000},
            {'name': 'Outdoor Garden', 'capacity': 100, 'space_type': 'outdoor', 'rate_per_hour': 8000},
        ]
        
        for space_data in default_spaces:
            EventSpace.objects.get_or_create(
                name=space_data['name'],
                defaults=space_data
            )
        
        self.stdout.write('Service data migration completed.')
    
    def migrate_activity_data(self):
        """Migrate existing activity data to new structure"""
        self.stdout.write('Migrating activity data...')
        
        # This would involve migrating existing user activity logs
        # to the new activity tracking system
        
        self.stdout.write('Activity data migration completed.')
```

---

## 7. Phase 6: Testing & Validation (Week 4)

### **7.1 Unit Tests**
```python
# resort_portal/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from resort_portal.models import *

class ResortDashboardTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_overview_page_loads(self):
        """Test that overview page loads correctly"""
        response = self.client.get(reverse('resort_portal:overview'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resort Overview')
    
    def test_guests_section_loads(self):
        """Test that guests section loads correctly"""
        response = self.client.get(reverse('resort_portal:guests'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Guest')
    
    def test_restaurant_section_loads(self):
        """Test that restaurant section loads correctly"""
        response = self.client.get(reverse('resort_portal:restaurant'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Table Management')
    
    def test_bar_section_loads(self):
        """Test that bar section loads correctly"""
        response = self.client.get(reverse('resort_portal:bar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bar Seating')
    
    def test_events_section_loads(self):
        """Test that events section loads correctly"""
        response = self.client.get(reverse('resort_portal:events'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Space Availability')
    
    def test_day_visitors_section_loads(self):
        """Test that day visitors section loads correctly"""
        response = self.client.get(reverse('resort_portal:day_visitors'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visitor Check-in')
    
    def test_sidebar_navigation(self):
        """Test sidebar navigation works correctly"""
        response = self.client.get(reverse('resort_portal:overview'))
        self.assertContains(response, 'Overview')
        self.assertContains(response, 'Room Guests')
        self.assertContains(response, 'Restaurant')
        self.assertContains(response, 'Bar')
        self.assertContains(response, 'Events & Spaces')
        self.assertContains(response, 'Day Visitors')
    
    def test_tab_navigation(self):
        """Test tab navigation works correctly"""
        response = self.client.get(reverse('resort_portal:guests') + '?tab=current-guests')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Current Guests')
```

### **7.2 Performance Tests**
```python
# resort_portal/tests_performance.py
from django.test import TestCase, Client
from django.test.utils import override_settings
from django.urls import reverse
import time

class PerformanceTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_overview_page_performance(self):
        """Test overview page load time"""
        start_time = time.time()
        response = self.client.get(reverse('resort_portal:overview'))
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(load_time, 2.0, "Overview page should load in under 2 seconds")
    
    def test_guests_section_performance(self):
        """Test guests section load time"""
        start_time = time.time()
        response = self.client.get(reverse('resort_portal:guests'))
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(load_time, 1.5, "Guests section should load in under 1.5 seconds")
    
    def test_restaurant_section_performance(self):
        """Test restaurant section load time"""
        start_time = time.time()
        response = self.client.get(reverse('resort_portal:restaurant'))
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(load_time, 1.5, "Restaurant section should load in under 1.5 seconds")
```

### **7.3 Integration Tests**
```python
# resort_portal/tests_integration.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from resort_portal.models import *

class IntegrationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
    
    def test_guest_check_in_flow(self):
        """Test complete guest check-in flow"""
        # Navigate to guests section
        response = self.client.get(reverse('resort_portal:guests'))
        self.assertEqual(response.status_code, 200)
        
        # Submit guest check-in form
        response = self.client.post(reverse('resort_portal:guests'), {
            'guest_name': 'John Doe',
            'phone_number': '+254712345678',
            'room_number': '1',
            'guest_type': 'overnight',
        })
        
        # Verify guest was created
        self.assertTrue(Guest.objects.filter(name='John Doe').exists())
    
    def test_restaurant_table_management_flow(self):
        """Test restaurant table management flow"""
        # Navigate to restaurant section
        response = self.client.get(reverse('resort_portal:restaurant'))
        self.assertEqual(response.status_code, 200)
        
        # Test table status update
        table = RestaurantTable.objects.first()
        response = self.client.post(reverse('resort_portal:restaurant'), {
            'action': 'update_table_status',
            'table_id': table.id,
            'status': 'occupied',
        })
        
        # Verify table status was updated
        table.refresh_from_db()
        self.assertEqual(table.status, 'occupied')
```

---

## 8. Phase 7: Go-Live & Monitoring (Week 4)

### **8.1 Deployment Checklist**
```bash
#!/bin/bash
# deployment_checklist.sh

echo "=== Resort Dashboard Deployment Checklist ==="

# 1. Backup current system
echo "1. Creating backup..."
python manage.py dumpdata resort_portal > pre_deployment_backup_$(date +%Y%m%d_%H%M%S).json

# 2. Run migrations
echo "2. Running migrations..."
python manage.py migrate resort_portal

# 3. Collect static files
echo "3. Collecting static files..."
python manage.py collectstatic --noinput

# 4. Check system health
echo "4. Checking system health..."
python manage.py check --deploy

# 5. Run tests
echo "5. Running tests..."
python manage.py test resort_portal

# 6. Restart services
echo "6. Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "=== Deployment completed ==="
```

### **8.2 Monitoring Setup**
```python
# resort_portal/monitoring.py
import time
import logging
from django.db import connection
from django.core.cache import cache

logger = logging.getLogger(__name__)

class DashboardMonitor:
    def __init__(self):
        self.metrics = {}
    
    def track_page_load_time(self, page_name, load_time):
        """Track page load times"""
        cache_key = f'dashboard_load_time_{page_name}'
        cache.set(cache_key, load_time, timeout=300)
        
        # Log slow pages
        if load_time > 2.0:
            logger.warning(f"Slow page load: {page_name} took {load_time:.2f}s")
    
    def track_database_queries(self, page_name, query_count):
        """Track database query count"""
        cache_key = f'dashboard_queries_{page_name}'
        cache.set(cache_key, query_count, timeout=300)
        
        # Log high query counts
        if query_count > 50:
            logger.warning(f"High query count: {page_name} executed {query_count} queries")
    
    def track_user_activity(self, user_id, action, page):
        """Track user activity"""
        cache_key = f'user_activity_{user_id}'
        activities = cache.get(cache_key, [])
        activities.append({
            'action': action,
            'page': page,
            'timestamp': time.time()
        })
        cache.set(cache_key, activities, timeout=3600)
    
    def get_performance_report(self):
        """Generate performance report"""
        report = {
            'page_load_times': {},
            'database_queries': {},
            'user_activities': {}
        }
        
        # Collect metrics from cache
        for key in cache.keys('dashboard_load_time_*'):
            page_name = key.replace('dashboard_load_time_', '')
            report['page_load_times'][page_name] = cache.get(key)
        
        for key in cache.keys('dashboard_queries_*'):
            page_name = key.replace('dashboard_queries_', '')
            report['database_queries'][page_name] = cache.get(key)
        
        return report
```

### **8.3 Rollback Plan**
```bash
#!/bin/bash
# rollback_plan.sh

echo "=== Resort Dashboard Rollback Plan ==="

# 1. Restore database
echo "1. Restoring database..."
python manage.py loaddata pre_deployment_backup_$(date +%Y%m%d).json

# 2. Reverse migrations
echo "2. Reversing migrations..."
python manage.py migrate resort_portal 0019

# 3. Restore templates
echo "3. Restoring templates..."
rm -rf templates/resort_portal
mv templates/resort_portal_backup_$(date +%Y%m%d) templates/resort_portal

# 4. Restart services
echo "4. Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "=== Rollback completed ==="
```

---

## 9. Phase 8: User Training & Documentation (Week 4)

### **9.1 User Training Materials**
```markdown
# Resort Dashboard User Training Guide

## Overview
The new Resort Dashboard provides a modular approach to managing all resort operations.

## Navigation
- **Overview**: Quick summary of all resort operations
- **Guest Operations**: Room guests and room management
- **Customer Operations**: Restaurant, bar, events, day visitors
- **Services**: All resort services
- **Reports**: Analytics and reports (managers only)
- **Settings**: System configuration

## Quick Actions
1. **Guest Check-In**: Navigate to Guests → Add Guest
2. **Restaurant Management**: Navigate to Restaurant → Table Management
3. **Bar Operations**: Navigate to Bar → Bar Seating
4. **Event Booking**: Navigate to Events & Spaces → Space Availability
5. **Day Visitor Check-In**: Navigate to Day Visitors → Visitor Check-in

## Common Workflows

### Guest Check-In Workflow
1. Go to Guests section
2. Click "Add Guest" tab
3. Enter guest information
4. Select room number
5. Click "Check-In Guest"

### Restaurant Seating Workflow
1. Go to Restaurant section
2. Click "Table Management" tab
3. View table availability
4. Click "Seat Walk-in" for available tables
5. Enter customer details
6. Assign table

### Bar Tab Management Workflow
1. Go to Bar section
2. Click "Bar Seating" tab
3. Click "Seat Customer" for available seats
4. Enter customer details
5. Assign seat
6. Add drinks to tab as needed

## Troubleshooting

### Common Issues
1. **Page not loading**: Check internet connection, refresh page
2. **Data not updating**: Click refresh button
3. **Can't find feature**: Check sidebar navigation
4. **Error messages**: Contact system administrator

### Getting Help
- Email: support@campopawa.com
- Phone: +254 700 000 000
- Documentation: Available in Settings → Help
```

### **9.2 Admin Training Materials**
```markdown
# Resort Dashboard Admin Guide

## System Administration

### User Management
1. Navigate to Settings → User Management
2. Add new users with appropriate roles
3. Set permissions for each role
4. Monitor user activity in Reports

### Configuration
1. Navigate to Settings → System Configuration
2. Update resort information
3. Configure room types and rates
4. Set up service categories
5. Configure email notifications

### Monitoring
1. Check Overview dashboard daily
2. Review Reports section weekly
3. Monitor system performance
4. Address user feedback promptly

### Maintenance
1. Regular database backups
2. Update system software
3. Monitor storage capacity
4. Review security logs
```

---

## 10. Success Metrics & KPIs

### **10.1 Performance Metrics**
- **Page Load Time**: < 2 seconds for all pages
- **Database Queries**: < 50 queries per page
- **User Satisfaction**: > 90% positive feedback
- **System Uptime**: > 99.5%

### **10.2 Usage Metrics**
- **Daily Active Users**: Track user engagement
- **Feature Adoption**: Monitor which features are used most
- **Task Completion Time**: Measure efficiency improvements
- **Error Rates**: Track and minimize system errors

### **10.3 Business Metrics**
- **Revenue Growth**: Track revenue from all sources
- **Operational Efficiency**: Measure time savings
- **Customer Satisfaction**: Monitor guest feedback
- **Staff Productivity**: Track staff performance

---

## 11. Timeline Summary

### **Week 1: Infrastructure & Overview**
- Set up new URL structure
- Create base templates
- Implement overview dashboard
- Set up navigation

### **Week 2: Guest Operations**
- Implement guests section
- Implement rooms section
- Test guest workflows
- Train staff on guest operations

### **Week 3: Customer Operations**
- Implement restaurant section
- Implement bar section
- Implement events section
- Implement day visitors section

### **Week 4: Integration & Go-Live**
- Complete data migration
- Run comprehensive tests
- Deploy to production
- User training and documentation

---

## 12. Risk Management

### **12.1 Technical Risks**
- **Data Loss**: Mitigated by comprehensive backups
- **Performance Issues**: Addressed by performance testing
- **Compatibility Issues**: Resolved by thorough testing
- **Security Vulnerabilities**: Addressed by security reviews

### **12.2 Operational Risks**
- **User Resistance**: Mitigated by comprehensive training
- **Workflow Disruption**: Minimized by phased rollout
- **Staff Confusion**: Addressed by clear documentation
- **Customer Impact**: Minimized by thorough testing

### **12.3 Business Risks**
- **Revenue Impact**: Monitored and addressed quickly
- **Customer Satisfaction**: Tracked and improved continuously
- **Competitive Disadvantage**: Mitigated by feature improvements
- **Compliance Issues**: Addressed by regular audits

---

## Conclusion

This transition guide provides a comprehensive roadmap for migrating from the current all-in-one dashboard to the new modular, section-based design. The phased approach ensures minimal disruption to operations while delivering significant improvements in usability, performance, and functionality.

**Key Success Factors:**
- Comprehensive planning and preparation
- Phased implementation with testing
- Thorough user training and support
- Continuous monitoring and improvement
- Clear rollback procedures

**Expected Benefits:**
- 10x faster page load times
- Improved user satisfaction
- Better operational efficiency
- Enhanced scalability and maintainability
- Complete resort operations coverage

The transition will position the resort dashboard as a modern, efficient, and comprehensive management platform that supports all aspects of resort operations.
