CREATE DATABASE university_erp;
USE university_erp;

CREATE TABLE Departments (
    DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
    DepartmentName VARCHAR(100) NOT NULL UNIQUE,
    HeadOfDepartment VARCHAR(100)
);

CREATE TABLE Programs (
    ProgramID INT AUTO_INCREMENT PRIMARY KEY,
    ProgramName VARCHAR(100) NOT NULL UNIQUE,
    DepartmentID INT NOT NULL,
    DegreeType ENUM('Bachelors', 'Masters', 'Doctoral') NOT NULL,
    Duration INT NOT NULL,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);

CREATE TABLE Users (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    Username VARCHAR(50) NOT NULL UNIQUE,
    Password VARCHAR(100) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Role ENUM('Student', 'Faculty', 'Staff') NOT NULL,
    DepartmentID INT,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);

CREATE TABLE Students (
    StudentID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    DateOfBirth DATE NOT NULL,
    Address VARCHAR(200) NOT NULL,
    ContactInfo VARCHAR(100) NOT NULL,
    EnrollmentStatus ENUM('Active', 'Inactive') NOT NULL,
    ProgramID INT NOT NULL,
    DepartmentID INT NOT NULL,
    FOREIGN KEY (ProgramID) REFERENCES Programs(ProgramID),
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);

CREATE TABLE Faculty (
    FacultyID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    DepartmentID INT NOT NULL,
    ContactInfo VARCHAR(100) NOT NULL,
    Specialization VARCHAR(100),
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);

CREATE TABLE Courses (
    CourseID INT AUTO_INCREMENT PRIMARY KEY,
    CourseName VARCHAR(100) NOT NULL,
    CourseCode VARCHAR(20) NOT NULL UNIQUE,
    Credits INT NOT NULL,
    DepartmentID INT NOT NULL,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);

CREATE TABLE Classes (
    ClassID INT AUTO_INCREMENT PRIMARY KEY,
    CourseID INT NOT NULL,
    Section VARCHAR(10) NOT NULL,
    Semester ENUM('Fall', 'Spring', 'Summer') NOT NULL,
    Year YEAR NOT NULL,
    FacultyID INT NOT NULL,
    Classroom VARCHAR(20),
    Schedule VARCHAR(100),
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID),
    FOREIGN KEY (FacultyID) REFERENCES Faculty(FacultyID)
);

CREATE TABLE Enrollments (
    EnrollmentID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    ClassID INT NOT NULL,
    Grade DECIMAL(4,2),
    Attendance DECIMAL(5,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID)
);

CREATE TABLE Fees (
    FeeID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    FeeType ENUM('Tuition', 'Hostel', 'Library', 'Other') NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    DueDate DATE NOT NULL,
    PaidDate DATE,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
);

CREATE TABLE Resources (
    ResourceID INT AUTO_INCREMENT PRIMARY KEY,
    ResourceType ENUM('Book', 'Journal', 'Equipment', 'Other') NOT NULL,
    Title VARCHAR(200) NOT NULL,
    Author VARCHAR(100),
    Manufacturer VARCHAR(100),
    Availability BOOLEAN NOT NULL,
    DepartmentID INT NOT NULL,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);

CREATE TABLE Events (
    EventID INT AUTO_INCREMENT PRIMARY KEY,
    EventName VARCHAR(100) NOT NULL,
    EventType ENUM('Seminar', 'Workshop', 'Conference', 'Other') NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    Venue VARCHAR(100) NOT NULL,
    Organizer VARCHAR(100) NOT NULL
);

CREATE TABLE Announcements (
    AnnouncementID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(200) NOT NULL,
    Description TEXT NOT NULL,
    AnnouncementDate DATE NOT NULL,
    Audience ENUM('Students', 'Faculty', 'Staff', 'All') NOT NULL
);

CREATE TABLE Attendance (
    AttendanceID INT AUTO_INCREMENT PRIMARY KEY,
    StudentID INT NOT NULL,
    ClassID INT NOT NULL,
    AttendanceDate DATE NOT NULL,
    Status ENUM('Present', 'Absent', 'Late') NOT NULL,
    FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
    FOREIGN KEY (ClassID) REFERENCES Classes(ClassID)
);

CREATE TABLE LearningManagement (
    LMSID INT AUTO_INCREMENT PRIMARY KEY,
    CourseID INT NOT NULL,
    LearningMaterials TEXT,
    Assignments TEXT,
    Discussions TEXT,
    Grades DECIMAL(4,2),
    FOREIGN KEY (CourseID) REFERENCES Courses(CourseID)
);