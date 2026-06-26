import os
import sys
from datetime import datetime, timedelta
from database.db import SessionLocal, engine, Base
from models.user import User
from models.book import Book
from models.loan import Loan
from models.request import BorrowRequest
from models.settings import Settings
from utils.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.query(Book).delete()
        db.query(Loan).delete()
        db.query(BorrowRequest).delete()
        db.query(Settings).delete()
        db.commit()

        settings = Settings(
            loan_period_days=14,
            max_books=3,
            fine_per_day=2.0,
            max_renewals=2
        )
        db.add(settings)
        
        hashed_password = get_password_hash("library@2024")

        admin = User(
            name="Library Admin",
            email="admin@college.edu",
            phone="9999999999",
            password_hash=hashed_password,
            role="admin"
        )
        db.add(admin)

        students_data = [
            ('Arjun Kumar', 'STU-001', 'arjun@college.edu', '9876543210', 'CSE', '3rd Year'),
            ('Priya Sharma', 'STU-002', 'priya@college.edu', '9876543211', 'ECE', '2nd Year'),
            ('Rahul Verma', 'STU-003', 'rahul@college.edu', '9876543212', 'MECH', '4th Year'),
            ('Sneha Reddy', 'STU-004', 'sneha@college.edu', '9876543213', 'CSE', '1st Year'),
            ('Kiran Nair', 'STU-005', 'kiran@college.edu', '9876543214', 'CSE', '3rd Year'),
            ('Amit Joshi', 'STU-006', 'amit@college.edu', '9876543215', 'EEE', '3rd Year'),
            ('Divya Patel', 'STU-007', 'divya@college.edu', '9876543216', 'CIVIL', '2nd Year'),
            ('Fazil Ahmed', 'STU-008', 'fazil@college.edu', '9876543217', 'CSE', '4th Year'),
            ('Anjali Sen', 'STU-009', 'anjali@college.edu', '9876543218', 'ECE', '1st Year'),
            ('Rohit Singh', 'STU-010', 'rohit@college.edu', '9876543219', 'MECH', '2nd Year'),
            ('Neha Gupta', 'STU-011', 'neha@college.edu', '9876543220', 'CIVIL', '3rd Year'),
            ('Vikram Rao', 'STU-012', 'vikram@college.edu', '9876543221', 'EEE', '4th Year'),
            ('Sonia Das', 'STU-013', 'sonia@college.edu', '9876543222', 'MBA', '1st Year'),
            ('Karan Malhotra', 'STU-014', 'karan@college.edu', '9876543223', 'MBA', '2nd Year'),
            ('Pooja Mehta', 'STU-015', 'pooja@college.edu', '9876543224', 'CSE', '2nd Year'),
            ('Aditya Goel', 'STU-016', 'aditya@college.edu', '9876543225', 'ECE', '3rd Year'),
            ('Ritu Sethi', 'STU-017', 'ritu@college.edu', '9876543226', 'CIVIL', '4th Year'),
            ('Varun Dhawan', 'STU-018', 'varun@college.edu', '9876543227', 'MECH', '1st Year'),
            ('Shreya Ghoshal', 'STU-019', 'shreya@college.edu', '9876543228', 'CSE', '4th Year'),
            ('Arijit Singh', 'STU-020', 'arijit@college.edu', '9876543229', 'ECE', '2nd Year')
        ]
        
        students = []
        for name, m_id, email, phone, dept, yr in students_data:
            stu = User(
                name=name,
                member_id=m_id,
                email=email,
                phone=phone,
                department=dept,
                year=yr,
                password_hash=hashed_password,
                role="student"
            )
            db.add(stu)
            students.append(stu)
        
        db.commit()
        
        raw_books = [
            ['Hands-On Machine Learning','Aurélien Géron','978-1492032649','Technology',2022,"O'Reilly",4,'Best ML practical guide','B4',4.8,'ml,python,scikit'],
            ['Clean Code','Robert C. Martin','978-0132350884','Technology',2008,'Prentice Hall',5,'Write clean readable software','C2',4.9,'software,coding,best-practices'],
            ['Introduction to Algorithms','Cormen et al.','978-0262033848','Technology',2009,'MIT Press',3,'CLRS bible of algorithms','C5',4.7,'algorithms,cs,theory'],
            ['Deep Learning','Goodfellow et al.','978-0262035613','Technology',2016,'MIT Press',3,'Neural networks deep dive','B5',4.6,'deep-learning,neural-nets,ai'],
            ['Python Crash Course','Eric Matthes','978-1593279288','Technology',2019,'No Starch',5,'Python beginner guide','D1',4.5,'python,beginner,programming'],
            ['The Pragmatic Programmer','Hunt & Thomas','978-0135957059','Technology',2019,'Addison-Wesley',4,'Software craftsmanship','C3',4.8,'programming,career,software'],
            ['Artificial Intelligence','Stuart Russell','978-0136042594','Technology',2020,'Pearson',4,'AI comprehensive textbook','B1',4.7,'ai,machine-learning,textbook'],
            ['Data Science from Scratch','Joel Grus','978-1492041139','Technology',2019,"O'Reilly",3,'DS fundamentals','E3',4.3,'data-science,python,statistics'],
            ['Design Patterns','Gang of Four','978-0201633610','Technology',1994,'Addison-Wesley',3,'Software design patterns','C6',4.7,'design-patterns,oop,software'],
            ['The Art of Computer Programming','Donald Knuth','978-0201896831','Technology',2011,'Addison-Wesley',2,'Knuth masterwork','C7',4.8,'algorithms,theory,computer-science'],
            ['Sapiens','Yuval Harari','978-0062316110','History',2015,'Harper',4,'Brief history of humankind','A1',4.8,'history,humanity,evolution'],
            ['Guns Germs and Steel','Jared Diamond','978-0393317558','History',1997,'Norton',3,'Fate of human societies','A2',4.5,'history,civilization,geography'],
            ['The Rise and Fall of the Roman Empire','Edward Gibbon','978-0140437645','History',1776,'Penguin',2,'Classic Roman history','A3',4.4,'rome,empire,ancient-history'],
            ['A People History of the United States','Howard Zinn','978-0060838652','History',2003,'Harper',2,'US history from below','A4',4.3,'american-history,politics,society'],
            ['The Silk Roads','Peter Frankopan','978-1101946329','History',2015,'Vintage',2,'History through trade routes','A5',4.4,'silk-road,trade,world-history'],
            ['A Brief History of Time','Stephen Hawking','978-0553380163','Science',1988,'Bantam',4,'Space and time explained','S1',4.6,'physics,cosmology,space'],
            ['Cosmos','Carl Sagan','978-0345539434','Science',1980,'Ballantine',4,'The universe explained','S2',4.8,'astronomy,space,science'],
            ['The Selfish Gene','Richard Dawkins','978-0198788607','Science',1976,'Oxford',3,'Gene-centred evolution','S3',4.5,'biology,evolution,genetics'],
            ['A Short History of Nearly Everything','Bill Bryson','978-0767908184','Science',2003,'Broadway',3,'Science made fun','S4',4.7,'science,history,popular-science'],
            ['The Double Helix','James Watson','978-0743216302','Science',1968,'Touchstone',2,'DNA discovery story','S5',4.2,'dna,biology,discovery'],
            ['1984','George Orwell','978-0451524935','Fiction',1949,'Signet',6,'Dystopian classic','F1',4.9,'dystopia,classic,political'],
            ['Dune','Frank Herbert','978-0441013593','Fiction',1965,'Ace',4,'Sci-fi epic masterpiece','F2',4.9,'scifi,epic,classic'],
            ['Brave New World','Aldous Huxley','978-0060850524','Fiction',1932,'Harper',4,'Dystopia classic','F3',4.5,'dystopia,classic,scifi'],
            ['The Hitchhiker Guide to the Galaxy','Douglas Adams','978-0345391803','Fiction',1979,'Del Rey',4,'Sci-fi comedy classic','F4',4.7,'scifi,comedy,classic'],
            ['Foundation','Isaac Asimov','978-0553293357','Fiction',1951,'Bantam',3,'Galactic empire saga','F5',4.8,'scifi,asimov,epic'],
            ['The Great Gatsby','F. Scott Fitzgerald','978-0743273565','Literature',1925,'Scribner',5,'Jazz Age classic','L1',4.3,'classic,american,novel'],
            ['To Kill a Mockingbird','Harper Lee','978-0061935466','Literature',1960,'Harper',4,'American classic','L2',4.7,'classic,american,justice'],
            ['One Hundred Years of Solitude','Gabriel Garcia Marquez','978-0060883287','Literature',1967,'Harper',3,'Magical realism masterpiece','L3',4.7,'magical-realism,latin-american,classic'],
            ['Crime and Punishment','Fyodor Dostoevsky','978-0486415871','Literature',1866,'Dover',3,'Russian classic thriller','L4',4.6,'russian,classic,psychology'],
            ['Pride and Prejudice','Jane Austen','978-0141439518','Literature',1813,'Penguin',4,'English classic romance','L5',4.5,'classic,romance,english'],
            ['Thinking Fast and Slow','Daniel Kahneman','978-0374533557','Self-Help',2011,'FSG',3,'Decision psychology','SH1',4.7,'psychology,decision-making,behaviour'],
            ['Atomic Habits','James Clear','978-0735211292','Self-Help',2018,'Avery',4,'Habit formation','SH2',4.8,'habits,productivity,self-improvement'],
            ['The 7 Habits of Highly Effective People','Stephen Covey','978-1451639612','Self-Help',1989,'Free Press',3,'Personal effectiveness','SH3',4.5,'habits,effectiveness,leadership'],
            ['Rich Dad Poor Dad','Robert Kiyosaki','978-1612680194','Self-Help',1997,'Plata',4,'Financial literacy','SH4',4.3,'finance,money,investing'],
            ['How to Win Friends and Influence People','Dale Carnegie','978-0671027032','Self-Help',1936,'Simon & Schuster',3,'Interpersonal skills','SH5',4.4,'communication,people-skills,classic'],
            ['Wings of Fire','APJ Abdul Kalam','978-8173711466','Biography',1999,'Universities Press',6,'Inspiring autobiography','BG1',4.9,'autobiography,india,science'],
            ['The Story of My Experiments with Truth','Mahatma Gandhi','978-0807059098','Biography',1927,'Beacon',3,'Gandhi autobiography','BG2',4.7,'autobiography,india,philosophy'],
            ['Steve Jobs','Walter Isaacson','978-1451648539','Biography',2011,'Simon & Schuster',3,'Jobs biography','BG3',4.6,'biography,technology,leadership'],
            ['Elon Musk','Walter Isaacson','978-1982181284','Biography',2023,'Simon & Schuster',3,'Musk biography','BG4',4.4,'biography,technology,entrepreneurship'],
            ['The Diary of a Young Girl','Anne Frank','978-0553296983','Biography',1947,'Bantam',4,'WWII diary classic','BG5',4.8,'diary,wwii,history'],
            ['Introduction to Linear Algebra','Gilbert Strang','978-0980232776','Mathematics',2016,'Wellesley-Cambridge',3,'LA textbook','M1',4.6,'linear-algebra,mathematics,engineering'],
            ['Calculus','James Stewart','978-1285740621','Mathematics',2015,'Cengage',3,'Calculus textbook','M2',4.4,'calculus,mathematics,textbook'],
            ['Discrete Mathematics','Kenneth Rosen','978-0073383095','Mathematics',2011,'McGraw-Hill',3,'DM for CS','M3',4.3,'discrete-math,cs,logic'],
            ['The Art of Problem Solving Vol 1','Sandor Lehoczky','978-0977304561','Mathematics',2006,'Art of Problem Solving',2,'Competition math','M4',4.7,'competition-math,problem-solving'],
            ['Probability and Statistics','Morris DeGroot','978-0321500465','Mathematics',2012,'Pearson',3,'Prob & Stats textbook','M5',4.2,'probability,statistics,mathematics'],
            ['The Republic','Plato','978-0872201361','Philosophy',380,'Hackett',4,'Political philosophy classic','P1',4.5,'philosophy,plato,politics'],
            ['Thus Spoke Zarathustra','Friedrich Nietzsche','978-0140441185','Philosophy',1883,'Penguin',3,'Nietzsche masterwork','P2',4.4,'philosophy,nietzsche,existentialism'],
            ['Meditations','Marcus Aurelius','978-0812968255','Philosophy',180,'Modern Library',3,'Stoic wisdom','P3',4.7,'stoicism,philosophy,wisdom'],
            ['The Problems of Philosophy','Bertrand Russell','978-0195002119','Philosophy',1912,'Oxford',2,'Philosophy intro','P4',4.3,'philosophy,russell,introduction'],
            ['Being and Time','Martin Heidegger','978-0061575594','Philosophy',1927,'Harper',2,'Existentialist philosophy','P5',4.2,'philosophy,existentialism,heidegger']
        ]

        books = []
        for b in raw_books:
            new_book = Book(
                title=b[0],
                author=b[1],
                isbn=b[2],
                genre=b[3],
                year=b[4],
                publisher=b[5],
                copies=b[6],
                available_copies=b[6],
                description=b[7],
                shelf_location=b[8],
                rating=b[9],
                tags=b[10]
            )
            db.add(new_book)
            books.append(new_book)
            
        db.commit()

        today = datetime.utcnow()
        
        # 15 returned loans
        for i in range(15):
            student_id = students[i].id
            book_id = books[i].id
            issue_date = (today - timedelta(days=20)).strftime("%Y-%m-%d")
            due_date = (today - timedelta(days=6)).strftime("%Y-%m-%d")
            return_date = (today - timedelta(days=8)).strftime("%Y-%m-%d")
            
            loan = Loan(
                user_id=student_id,
                book_id=book_id,
                issue_date=issue_date,
                due_date=due_date,
                return_date=return_date,
                renew_count=0,
                status="returned",
                fine_amount=0.0
            )
            db.add(loan)
            
        # 3 active loans
        for i in range(3):
            student_id = students[15 + i].id
            book_id = books[15 + i].id
            issue_date = (today - timedelta(days=5)).strftime("%Y-%m-%d")
            due_date = (today + timedelta(days=9)).strftime("%Y-%m-%d")
            
            loan = Loan(
                user_id=student_id,
                book_id=book_id,
                issue_date=issue_date,
                due_date=due_date,
                return_date=None,
                renew_count=0,
                status="active",
                fine_amount=0.0
            )
            db.add(loan)
            books[15 + i].available_copies -= 1
            
        # 2 overdue loans
        for i in range(2):
            student_id = students[18 + i].id
            book_id = books[18 + i].id
            issue_date = (today - timedelta(days=20)).strftime("%Y-%m-%d")
            due_date = (today - timedelta(days=6)).strftime("%Y-%m-%d")
            
            loan = Loan(
                user_id=student_id,
                book_id=book_id,
                issue_date=issue_date,
                due_date=due_date,
                return_date=None,
                renew_count=0,
                status="overdue",
                fine_amount=12.0
            )
            db.add(loan)
            books[18 + i].available_copies -= 1
            
        # 10 pending requests
        for i in range(10):
            student_id = students[i].id
            book_id = books[20 + i].id
            preferred_date = (today + timedelta(days=2)).strftime("%Y-%m-%d")
            
            req = BorrowRequest(
                user_id=student_id,
                book_id=book_id,
                preferred_date=preferred_date,
                note="Need this book for exams.",
                status="pending"
            )
            db.add(req)

        db.commit()
        print("Database seeded successfully!")
        print(f"Admin created: admin / library@2024")
        print(f"Books created: {len(books)}")
        print(f"Students created: {len(students)}")
        print(f"Loans created: 20")
        print(f"Pending requests created: 10")
        
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
