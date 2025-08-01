#!/usr/bin/env python3
"""
Apple Help Desk Database Manager
Generates SQLite database and provides utility functions for ITSM operations
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json

class AppleHelpDeskDB:
    def __init__(self, db_path: str = "apple_helpdesk.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        self.conn = None
        self.connect()
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def create_database(self):
        """Create database schema with sample data"""
        schema_sql = """
        -- Apple Authorized Support Help Desk Database Schema
        -- SQLite Database for Agentic RAG POC

        -- Enable foreign key constraints
        PRAGMA foreign_keys = ON;

        -- Categories for organizing tickets
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Product lines and models
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_line VARCHAR(50) NOT NULL,
            model VARCHAR(100) NOT NULL,
            release_year INTEGER,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Customer information
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(20),
            apple_id VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Support agents
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            employee_id VARCHAR(50) UNIQUE NOT NULL,
            specialization VARCHAR(100),
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Support tickets/cases
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number VARCHAR(20) UNIQUE NOT NULL,
            customer_id INTEGER NOT NULL,
            agent_id INTEGER,
            category_id INTEGER NOT NULL,
            product_id INTEGER,
            subject VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            priority VARCHAR(20) DEFAULT 'Medium',
            status VARCHAR(20) DEFAULT 'Open',
            serial_number VARCHAR(100),
            ios_version VARCHAR(20),
            resolution TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_at DATETIME,
            closed_at DATETIME,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        -- Ticket comments/notes
        CREATE TABLE IF NOT EXISTS ticket_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            agent_id INTEGER,
            comment_type VARCHAR(20) DEFAULT 'note',
            content TEXT NOT NULL,
            is_public BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES tickets(id),
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        );

        -- Knowledge base articles
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            category_id INTEGER,
            product_id INTEGER,
            tags VARCHAR(500),
            is_published BOOLEAN DEFAULT 1,
            view_count INTEGER DEFAULT 0,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (created_by) REFERENCES agents(id)
        );

        -- SLA definitions
        CREATE TABLE IF NOT EXISTS sla_policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            priority VARCHAR(20) NOT NULL,
            response_time_hours INTEGER NOT NULL,
            resolution_time_hours INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_tickets_customer ON tickets(customer_id);
        CREATE INDEX IF NOT EXISTS idx_tickets_agent ON tickets(agent_id);
        CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
        CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);
        CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at);
        CREATE INDEX IF NOT EXISTS idx_ticket_comments_ticket ON ticket_comments(ticket_id);
        CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category_id);
        CREATE INDEX IF NOT EXISTS idx_knowledge_base_product ON knowledge_base(product_id);

        -- Create a view for ticket summary
        CREATE VIEW IF NOT EXISTS ticket_summary AS
        SELECT 
            t.id,
            t.ticket_number,
            c.first_name || ' ' || c.last_name AS customer_name,
            c.email AS customer_email,
            a.first_name || ' ' || a.last_name AS agent_name,
            cat.name AS category,
            p.product_line || ' ' || p.model AS product,
            t.subject,
            t.priority,
            t.status,
            t.created_at,
            t.updated_at
        FROM tickets t
        LEFT JOIN customers c ON t.customer_id = c.id
        LEFT JOIN agents a ON t.agent_id = a.id
        LEFT JOIN categories cat ON t.category_id = cat.id
        LEFT JOIN products p ON t.product_id = p.id;
        """
        
        try:
            # Execute schema creation
            self.conn.executescript(schema_sql)
            self.conn.commit()
            print("Database schema created successfully")
            
            # Insert sample data
            self._insert_sample_data()
            print("Sample data inserted successfully")
            
        except sqlite3.Error as e:
            print(f"Error creating database: {e}")
            raise
    
    def _insert_sample_data(self):
        """Insert sample data into tables"""
        
        # Check if data already exists
        cursor = self.conn.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] > 0:
            print("Sample data already exists, skipping insertion")
            return
        
        sample_data = {
            'categories': [
                ('Hardware Issues', 'Physical device problems, damage, malfunction'),
                ('Software Issues', 'iOS, macOS, app-related problems'),
                ('Account & Security', 'Apple ID, iCloud, security concerns'),
                ('Connectivity', 'Wi-Fi, Bluetooth, cellular connectivity issues'),
                ('Performance', 'Slow performance, battery, storage issues'),
                ('Setup & Configuration', 'Initial setup, configuration assistance'),
                ('Warranty & Repair', 'Warranty claims, repair requests')
            ],
            'products': [
                ('iPhone', 'iPhone 15 Pro Max', 2023, 1),
                ('iPhone', 'iPhone 15 Pro', 2023, 1),
                ('iPhone', 'iPhone 15', 2023, 1),
                ('iPhone', 'iPhone 14 Pro Max', 2022, 1),
                ('iPhone', 'iPhone 14', 2022, 1),
                ('iPhone', 'iPhone 13', 2021, 1),
                ('iPad', 'iPad Pro 12.9-inch (6th gen)', 2022, 1),
                ('iPad', 'iPad Air (5th gen)', 2022, 1),
                ('iPad', 'iPad (10th gen)', 2022, 1),
                ('Mac', 'MacBook Pro 16-inch (M3)', 2023, 1),
                ('Mac', 'MacBook Air 15-inch (M2)', 2023, 1),
                ('Mac', 'MacBook Air 13-inch (M2)', 2022, 1),
                ('Mac', 'iMac 24-inch (M3)', 2023, 1),
                ('Apple Watch', 'Apple Watch Series 9', 2023, 1),
                ('Apple Watch', 'Apple Watch Ultra 2', 2023, 1),
                ('AirPods', 'AirPods Pro (2nd gen)', 2022, 1),
                ('AirPods', 'AirPods (3rd gen)', 2021, 1)
            ],
            'customers': [
                ('John', 'Smith', 'john.smith@email.com', '+1-555-0123', 'john.smith@icloud.com'),
                ('Sarah', 'Johnson', 'sarah.johnson@email.com', '+1-555-0124', 'sarah.j@icloud.com'),
                ('Michael', 'Brown', 'michael.brown@email.com', '+1-555-0125', 'm.brown@icloud.com'),
                ('Emily', 'Davis', 'emily.davis@email.com', '+1-555-0126', 'emily.davis@icloud.com'),
                ('Robert', 'Wilson', 'robert.wilson@email.com', '+1-555-0127', 'r.wilson@icloud.com'),
                ('Lisa', 'Anderson', 'lisa.anderson@email.com', '+1-555-0128', 'lisa.anderson@icloud.com'),
                ('David', 'Taylor', 'david.taylor@email.com', '+1-555-0129', 'd.taylor@icloud.com'),
                ('Jennifer', 'Moore', 'jennifer.moore@email.com', '+1-555-0130', 'jen.moore@icloud.com')
            ],
            'agents': [
                ('Alex', 'Thompson', 'alex.thompson@applecare.com', 'EMP001', 'iOS Support'),
                ('Maria', 'Garcia', 'maria.garcia@applecare.com', 'EMP002', 'macOS Support'),
                ('James', 'Lee', 'james.lee@applecare.com', 'EMP003', 'Hardware Specialist'),
                ('Sophie', 'Chen', 'sophie.chen@applecare.com', 'EMP004', 'iOS Support'),
                ('Ryan', 'O\'Connor', 'ryan.oconnor@applecare.com', 'EMP005', 'Account & Security'),
                ('Amanda', 'White', 'amanda.white@applecare.com', 'EMP006', 'Hardware Specialist'),
                ('Carlos', 'Rodriguez', 'carlos.rodriguez@applecare.com', 'EMP007', 'macOS Support')
            ],
            'sla_policies': [
                ('Critical Priority SLA', 'Critical', 1, 4),
                ('High Priority SLA', 'High', 2, 8),
                ('Medium Priority SLA', 'Medium', 4, 24),
                ('Low Priority SLA', 'Low', 8, 72)
            ]
        }
        
        # Insert basic data
        for table, data in sample_data.items():
            if table == 'categories':
                self.conn.executemany("INSERT INTO categories (name, description) VALUES (?, ?)", data)
            elif table == 'products':
                self.conn.executemany("INSERT INTO products (product_line, model, release_year, is_active) VALUES (?, ?, ?, ?)", data)
            elif table == 'customers':
                self.conn.executemany("INSERT INTO customers (first_name, last_name, email, phone, apple_id) VALUES (?, ?, ?, ?, ?)", data)
            elif table == 'agents':
                self.conn.executemany("INSERT INTO agents (first_name, last_name, email, employee_id, specialization) VALUES (?, ?, ?, ?, ?)", data)
            elif table == 'sla_policies':
                self.conn.executemany("INSERT INTO sla_policies (name, priority, response_time_hours, resolution_time_hours) VALUES (?, ?, ?, ?)", data)
        
        # Insert sample tickets
        tickets_data = [
            ('APL-2024-001', 1, 1, 1, 1, 'iPhone screen flickering after drop', 'Customer reports screen flickering and unresponsive touch in bottom right corner after dropping device. No visible cracks but screen appears damaged internally.', 'High', 'In Progress', 'F2LLD2Q2Q8K1', '17.1.1'),
            ('APL-2024-002', 2, 2, 2, 11, 'MacBook won\'t boot after macOS update', 'After installing latest macOS update, MacBook shows black screen with spinning wheel and won\'t complete boot process. Tried safe mode without success.', 'Critical', 'Open', 'C02YW2Q2LVDT', 'macOS 14.1'),
            ('APL-2024-003', 3, 3, 5, 2, 'iPhone battery draining very quickly', 'Battery percentage drops from 100% to 20% within 3-4 hours of normal use. Started happening about a week ago. Battery health shows 89%.', 'Medium', 'Resolved', 'F2LLD3R3Q9K2', '17.1.1'),
            ('APL-2024-004', 4, 1, 4, 8, 'iPad not connecting to Wi-Fi', 'iPad cannot connect to home Wi-Fi network. Shows network but fails authentication. Other devices connect fine to same network.', 'Medium', 'Pending', 'DMPL2K3LD4M1', '17.1'),
            ('APL-2024-005', 5, 4, 3, None, 'Cannot sign into Apple ID', 'Getting error message "Apple ID or password incorrect" but credentials are correct. Tried password reset but still having issues.', 'High', 'Open', None, None),
            ('APL-2024-006', 6, 2, 2, 10, 'MacBook Pro running very slow', 'MacBook Pro has become extremely slow, taking minutes to open applications. Activity Monitor shows high CPU usage but no specific process consuming resources.', 'Medium', 'In Progress', 'C02ZW3Q3MVDT', 'macOS 14.1'),
            ('APL-2024-007', 7, 3, 1, 14, 'Apple Watch not charging', 'Apple Watch Series 9 stopped charging yesterday. Tried different charging cables and power adapters. Watch shows charging symbol but battery percentage doesn\'t increase.', 'High', 'Open', 'HX7J2L3MP4N2', 'watchOS 10.1'),
            ('APL-2024-008', 8, 5, 6, 4, 'Need help setting up new iPhone', 'Just purchased iPhone 14 Pro Max and need assistance with data transfer from old iPhone and setting up Face ID, Apple Pay, and iCloud backup.', 'Low', 'Resolved', 'F2LLD4S4Q1K3', '17.1.1')
        ]
        
        self.conn.executemany("""INSERT INTO tickets (ticket_number, customer_id, agent_id, category_id, product_id, subject, description, priority, status, serial_number, ios_version) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tickets_data)
        
        # Insert sample knowledge base articles
        kb_articles = [
            ('How to Force Restart Different iPhone Models', 
             'Force restarting your iPhone can resolve many software issues. Here are the steps for different models:\n\niPhone 8 and later:\n1. Press and quickly release Volume Up button\n2. Press and quickly release Volume Down button\n3. Press and hold Side button until Apple logo appears\n\niPhone 7 and 7 Plus:\n1. Press and hold Volume Down and Side buttons simultaneously\n2. Hold until Apple logo appears\n\niPhone 6s and earlier:\n1. Press and hold Home and Top (or Side) buttons simultaneously\n2. Hold until Apple logo appears\n\nThis process will not delete any data from your device.', 
             2, None, 'force restart,frozen,unresponsive,software issue', 1),
            ('Troubleshooting Wi-Fi Connection Issues on iOS Devices',
             'If your iPhone or iPad won\'t connect to Wi-Fi, try these steps in order:\n\n1. Check Wi-Fi is enabled in Settings > Wi-Fi\n2. Verify you\'re connecting to correct network and password is correct\n3. Restart your iOS device\n4. Reset Network Settings: Settings > General > Transfer or Reset iPhone > Reset > Reset Network Settings\n5. Forget and reconnect to network: Settings > Wi-Fi > tap (i) next to network > Forget This Network\n6. Update iOS to latest version\n7. Reset router/modem\n\nIf issues persist, contact your internet service provider.', 
             4, None, 'wifi,connection,network,internet,troubleshooting', 4)
        ]
        
        self.conn.executemany("INSERT INTO knowledge_base (title, content, category_id, product_id, tags, created_by) VALUES (?, ?, ?, ?, ?, ?)", kb_articles)
        
        self.conn.commit()
    
    # SEARCH UTILITY FUNCTIONS
    
    def search_tickets(self, **kwargs) -> List[Dict]:
        """
        Search tickets with various filters
        Args:
            customer_email: Filter by customer email
            agent_id: Filter by agent ID
            status: Filter by status
            priority: Filter by priority
            category: Filter by category name
            product_line: Filter by product line
            limit: Limit results (default 50)
        """
        query = """
        SELECT t.*, c.first_name || ' ' || c.last_name as customer_name, 
               c.email as customer_email, a.first_name || ' ' || a.last_name as agent_name,
               cat.name as category_name, p.product_line, p.model
        FROM tickets t
        LEFT JOIN customers c ON t.customer_id = c.id
        LEFT JOIN agents a ON t.agent_id = a.id
        LEFT JOIN categories cat ON t.category_id = cat.id
        LEFT JOIN products p ON t.product_id = p.id
        WHERE 1=1
        """
        params = []
        
        if 'customer_email' in kwargs:
            query += " AND c.email LIKE ?"
            params.append(f"%{kwargs['customer_email']}%")
        
        if 'agent_id' in kwargs:
            query += " AND t.agent_id = ?"
            params.append(kwargs['agent_id'])
            
        if 'status' in kwargs:
            query += " AND t.status = ?"
            params.append(kwargs['status'])
            
        if 'priority' in kwargs:
            query += " AND t.priority = ?"
            params.append(kwargs['priority'])
            
        if 'category' in kwargs:
            query += " AND cat.name LIKE ?"
            params.append(f"%{kwargs['category']}%")
            
        if 'product_line' in kwargs:
            query += " AND p.product_line LIKE ?"
            params.append(f"%{kwargs['product_line']}%")
        
        query += " ORDER BY t.created_at DESC"
        
        if 'limit' in kwargs:
            query += " LIMIT ?"
            params.append(kwargs['limit'])
        else:
            query += " LIMIT 50"
        
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def search_knowledge_base(self, search_term: str, category_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """Search knowledge base articles by content or tags"""
        query = """
        SELECT kb.*, cat.name as category_name, a.first_name || ' ' || a.last_name as author_name
        FROM knowledge_base kb
        LEFT JOIN categories cat ON kb.category_id = cat.id
        LEFT JOIN agents a ON kb.created_by = a.id
        WHERE kb.is_published = 1 AND (
            kb.title LIKE ? OR 
            kb.content LIKE ? OR 
            kb.tags LIKE ?
        )
        """
        params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
        
        if category_id:
            query += " AND kb.category_id = ?"
            params.append(category_id)
        
        query += " ORDER BY kb.view_count DESC, kb.updated_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_customer_by_email(self, email: str) -> Optional[Dict]:
        """Find customer by email address"""
        cursor = self.conn.execute("SELECT * FROM customers WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_agent_workload(self, agent_id: int) -> Dict:
        """Get agent's current workload statistics"""
        query = """
        SELECT 
            status,
            priority,
            COUNT(*) as count
        FROM tickets 
        WHERE agent_id = ? AND status IN ('Open', 'In Progress', 'Pending')
        GROUP BY status, priority
        """
        cursor = self.conn.execute(query, (agent_id,))
        workload = cursor.fetchall()
        
        # Get agent info
        agent_cursor = self.conn.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        agent = dict(agent_cursor.fetchone()) if agent_cursor.fetchone() else None
        
        return {
            'agent': agent,
            'workload': [dict(row) for row in workload],
            'total_active_tickets': sum(row['count'] for row in workload)
        }
    
    # PERSISTENCE UTILITY FUNCTIONS
    
    def create_ticket(self, customer_id: int, category_id: int, subject: str, description: str, 
                     priority: str = 'Medium', product_id: Optional[int] = None, 
                     serial_number: Optional[str] = None, ios_version: Optional[str] = None) -> str:
        """Create a new support ticket"""
        # Generate ticket number
        cursor = self.conn.execute("SELECT COUNT(*) FROM tickets WHERE ticket_number LIKE 'APL-2024-%'")
        count = cursor.fetchone()[0] + 1
        ticket_number = f"APL-2024-{count:03d}"
        
        query = """
        INSERT INTO tickets (ticket_number, customer_id, category_id, subject, description, 
                           priority, product_id, serial_number, ios_version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.conn.execute(query, (ticket_number, customer_id, category_id, subject, 
                                description, priority, product_id, serial_number, ios_version))
        self.conn.commit()
        
        print(f"Ticket {ticket_number} created successfully")
        return ticket_number
    
    def update_ticket_status(self, ticket_id: int, status: str, agent_id: Optional[int] = None, 
                           resolution: Optional[str] = None) -> bool:
        """Update ticket status and optionally assign agent or add resolution"""
        updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
        params = [status]
        
        if agent_id:
            updates.append("agent_id = ?")
            params.append(agent_id)
            
        if resolution:
            updates.append("resolution = ?")
            params.append(resolution)
            
        if status == 'Resolved':
            updates.append("resolved_at = CURRENT_TIMESTAMP")
        elif status == 'Closed':
            updates.append("closed_at = CURRENT_TIMESTAMP")
        
        query = f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?"
        params.append(ticket_id)
        
        cursor = self.conn.execute(query, params)
        self.conn.commit()
        
        success = cursor.rowcount > 0
        if success:
            print(f"Ticket {ticket_id} updated to status: {status}")
        return success
    
    def add_ticket_comment(self, ticket_id: int, content: str, agent_id: Optional[int] = None, 
                          comment_type: str = 'note', is_public: bool = False) -> int:
        """Add comment to ticket"""
        query = """
        INSERT INTO ticket_comments (ticket_id, agent_id, comment_type, content, is_public)
        VALUES (?, ?, ?, ?, ?)
        """
        
        cursor = self.conn.execute(query, (ticket_id, agent_id, comment_type, content, is_public))
        self.conn.commit()
        
        comment_id = cursor.lastrowid
        print(f"Comment added to ticket {ticket_id}")
        return comment_id
    
    def create_customer(self, first_name: str, last_name: str, email: str, 
                       phone: Optional[str] = None, apple_id: Optional[str] = None) -> int:
        """Create new customer record"""
        query = """
        INSERT INTO customers (first_name, last_name, email, phone, apple_id)
        VALUES (?, ?, ?, ?, ?)
        """
        
        cursor = self.conn.execute(query, (first_name, last_name, email, phone, apple_id))
        self.conn.commit()
        
        customer_id = cursor.lastrowid
        print(f"Customer {first_name} {last_name} created with ID: {customer_id}")
        return customer_id
    
    def create_kb_article(self, title: str, content: str, category_id: int, 
                         created_by: int, product_id: Optional[int] = None, 
                         tags: Optional[str] = None) -> int:
        """Create new knowledge base article"""
        query = """
        INSERT INTO knowledge_base (title, content, category_id, product_id, tags, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        cursor = self.conn.execute(query, (title, content, category_id, product_id, tags, created_by))
        self.conn.commit()
        
        article_id = cursor.lastrowid
        print(f"Knowledge base article '{title}' created with ID: {article_id}")
        return article_id
    
    def increment_kb_view_count(self, article_id: int):
        """Increment view count for knowledge base article"""
        self.conn.execute("UPDATE knowledge_base SET view_count = view_count + 1 WHERE id = ?", 
                         (article_id,))
        self.conn.commit()
    
    # REPORTING FUNCTIONS
    
    def get_ticket_statistics(self) -> Dict:
        """Get overall ticket statistics"""
        stats = {}
        
        # Status distribution
        cursor = self.conn.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
        stats['by_status'] = dict(cursor.fetchall())
        
        # Priority distribution
        cursor = self.conn.execute("SELECT priority, COUNT(*) FROM tickets GROUP BY priority")
        stats['by_priority'] = dict(cursor.fetchall())
        
        # Category distribution
        cursor = self.conn.execute("""
            SELECT c.name, COUNT(t.id) 
            FROM categories c 
            LEFT JOIN tickets t ON c.id = t.category_id 
            GROUP BY c.name
        """)
        stats['by_category'] = dict(cursor.fetchall())
        
        # SLA compliance (simplified)
        cursor = self.conn.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'Resolved' AND resolved_at IS NOT NULL THEN 1 END) as resolved,
                COUNT(*) as total
            FROM tickets
        """)
        row = cursor.fetchone()
        stats['resolution_rate'] = (row[0] / row[1] * 100) if row[1] > 0 else 0
        
        return stats

def main():
    """Main function to demonstrate database creation and usage"""
    print("=== Apple Help Desk Database Manager ===\n")
    
    # Initialize database
    db = AppleHelpDeskDB("apple_helpdesk.db")
    
    try:
        # Create database and schema
        if 1==0:
            print("Creating database schema...")
            db.create_database()
        
        # Demonstrate search functions
        print("\n=== Search Examples ===")
        
        # Search tickets by status
        open_tickets = db.search_tickets(status='Open', limit=3)
        print(f"\nFound {len(open_tickets)} open tickets:")
        for ticket in open_tickets:
            print(f"- {ticket['ticket_number']}: {ticket['subject']} ({ticket['priority']})")
        
        # Search knowledge base
        kb_results = db.search_knowledge_base('iPhone restart', limit=2)
        print(f"\nKnowledge base search results for 'iPhone restart':")
        for article in kb_results:
            print(f"- {article['title']}")
        
        # Get customer by email
        customer = db.get_customer_by_email('john.smith@email.com')
        if customer:
            print(f"\nCustomer found: {customer['first_name']} {customer['last_name']}")
        
        # Demonstrate persistence functions
        print("\n=== Persistence Examples ===")
        
        # Create new ticket
        if customer:
            new_ticket = db.create_ticket(
                customer_id=customer['id'],
                category_id=2,  # Software Issues
                subject='App crashing on iOS 17',
                description='Instagram app crashes every time I try to post a story',
                priority='Medium',
                product_id=1,  # iPhone 15 Pro Max
                ios_version='17.1.1'
            )
            print(f"New ticket created: {new_ticket}")
        
        # Get statistics
        print("\n=== Database Statistics ===")
        stats = db.get_ticket_statistics()
        print(f"Tickets by Status: {stats['by_status']}")
        print(f"Tickets by Priority: {stats['by_priority']}")
        print(f"Resolution Rate: {stats['resolution_rate']:.1f}%")
        
        # Demonstrate adding a comment
        if open_tickets:
            ticket_id = open_tickets[0]['id']
            db.add_ticket_comment(
                ticket_id=ticket_id,
                content="Customer contacted via phone. Scheduled remote diagnostic session.",
                agent_id=1,
                comment_type='note',
                is_public=True
            )
        
        print(f"\nDatabase created successfully at: {db.db_path}")
        print("You can now use this database for your Agentic RAG POC!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()