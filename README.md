# Project Management System (OOP + UML) — Lab Assignment

An object-oriented Project Management System where a company handles multiple
clients/projects and assigns specific employees to manage each project.

## Features
- Employee ↔ Project assignment (who handles which project)
- Project requirements tracking
- Development life-cycle tracker (Requirement Feasibility → Testing → Deployment → Maintenance)
- Project billing / invoicing
- Client feedback captured at every life-cycle stage
- Three polymorphic Project subclasses: `WebDevelopmentProject`, `MobileAppProject`, `DataScienceProject`

## Folder structure
```
pms_project/
├── src/
│   ├── pms.py        # all classes (the system)
│   └── demo.py        # driver script / demo
├── tests/
│   └── test_pms.py    # unit tests (14 test cases)
├── diagrams/
│   ├── uml.dot                 # Graphviz source
│   └── uml_class_diagram.png   # rendered UML class diagram
├── screenshots/
│   ├── terminal_output_screenshot.png
│   └── test_output_screenshot.png
└── README.md
```

## How to run
```bash
cd src
python3 demo.py
```

## How to run tests
```bash
cd tests
python3 test_pms.py -v
```

## Author
Prepared as part of an academic UML/OOP Lab Assignment.
