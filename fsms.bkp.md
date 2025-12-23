# Disclaimer

This document is a draft, and there is no guarantee regarding the correctness of its content. It is a work in progress, and constructive criticism is welcome.

# System Concept

The FSMS system assists field operators with their daily task execution. Its fundamental function is to serve as an intermediary between SAP work orders and OMS incident tickets on one side and field operators on the other. These SAP modules and the OMS are collectively known as source systems.

## The Data Flow

SAP modules and OMS system - aka source systems, executes the business ERP processes, monitors electric and gas grid, and collect feedback from customer interactions, creating work orders and incident tickets.

When FSMS server receive a call from a source system, creates tasks to be executed by field teams, based on rules manged by business consultants, then are enlisted to a specific centre, based on call target location.

On center there is a dispatcher that takes care to assign tasks to field teams from his area.

![System Data Flow](system-data-circle.png)

The mobile application retrieves the team's assigned tasks and associate specific workflows.

Assisted by flows, the field teams solve the problems then creates relevant ERP documents and sends them to DMS and FSMS servers. Subsequently, the FSMS server creates order status and forwards it back to originator source system, thus completing the entire cycle.

## Functional Description

FSMS server collects work orders from certain SAP modules. But before that, FSMS server is configured by business consultants and coordination centre dispatchers. Because FSMS server administration is performed with back office application, business consultants and centre dispatchers are collectively named back office operators. Part of this group are also the members of the FSMS support team.

Based on work order attributes and some business rules, known as Data Transform Layer (DTL), FSMS server creates actions required to fulfill a specific work order; in general for every work order a single action is created but, for more complex work orders DTL can be configured with multiple actions. This DTL acronym is a proprietary Globema abstraction and should not be confused with Data Transform Language, which is associated with processing business documents in XML.

Every action has a location inherited from work order. Based on this location and on geographical area configured on coordination centre, FSMS server enroll the actions to certain centre. The center dispatcher assigns actions to field teams using a Gantt chart, considering factors like team type, calendar and skills. Also dispatcher should take care to assign actions and the right order to minimize the time required to travel to locations.

FSMS server has an _optimizer_ able to assign actions automatically but is not know how often is used. This optimizer is probably using some implementation of the _shortest path algorithm_.

OMS system generates tickets that are processed by FSMS server in a similar manner. Ticket is converted into an action then action is assigned and sorted using above steps.

Beside actions created from orders, back office operator is able to create actions on FSMS server directly, actions named _FFA Action_. Once created on FSMS server, FFA action is processed as described above.

![System Overview](system-overview.png)

FSMS mobile application uses `GetActions_Mobile` endpoint to retrieve team's actions list from FSMS server. On the mobile application actions are converted into an internal representation named _Task_, after that a flow is attached; a flow is a description of the steps that field operator follows in order to fulfill the task. Task's flows are displayed on user interface, step by step, sending task status events to server endpoint `ReportEvent_Mobile`.

After the flow ends and the task is complete, field operator may need to create related documents like observation notes and minutes. These documents are uploaded from mobile application to external documents management server. Also a notification about work order status is sent to source system (SAP modules or OMS) via FSMS server endpoint `SendIsuOs_Mobile`, which forwards this notification.

To ensure uninterrupted service, the mobile application must have offline capabilities. After the actions list is loaded, typically at the beginning of the workday at the team center, the mobile application can execute task flows even when offline.

## Data Transformation Layer

## Task Sequence

Below is a sequence diagram illustrating the online processing of a SAP work order, following the same logical flow as described earlier.

![Task Sequence Diagram](task-sequence.png)

For completeness here is the description of the above diagram:
- SAP sends a work order to the FSMS server.
- The FSMS server converts the work order into an action and updates the respective team's actions list.
- FSMS mobile application retrieves the team's actions list, subsequently converting these actions into tasks and associating them with flows.
- The field operator executes flows step by step, while in background, mobile application sends task status events to the FSMS server.
- On task complete a notification about order status is sent to source system via FSMS server endpoint `SendIsuOs_Mobile`, which forwards this notification.

Please bear in mind that discussed sequence is just a sample and that different tasks may have pretty different sequences of messages.

# FSMS Overview

The FSMS system follows a traditional client-server architecture, employing the SOAP and REST protocols over HTTP(S) for message transmission. SOAP is used for core task processing whereas REST for couple of auxiliary uses. The back office servers are not directly accessible from public networks. Instead, a secure VPN connection is in place to enable secure access to these servers.

Both the client and server components are primarily developed in Java. Specifically, the mobile application - serving as the client, uses JavaFX technology, while the server implementation is based on the Apache Axis2 platform.

The mobile application runs on Windows tablets and incorporates an embedded database. Each user on the tablet has a dedicated database instance, which comes into play when the mobile application operates offline. User database data is initially fetched from backend servers and continuously synchronized while the tablet is online.

For user authentication, the mobile application retrieves user information from the operating system using the 'whoami' system command.

![FSMS Overview](fsms-overview.png)

On the server side, the structure includes application servers running on Apache Tomcat, and Oracle databases. Two instances of the application server are present behind a high-availability (HA) load balancer. The load balancer is set up with two servers in an active/standby configuration, linked to the same floating (virtual) IP address. Requests are directed to the application servers only by the active balancer. Load balancer keeps application servers loading even and knows to properly manages HTTP sessions.

Additionally, there are two databases in place, although only one is actively involved in processing current requests. The second database serves as an archival and reporting database, and it is updated via an ETL process sourced from the working database.

External systems, such as SAP modules and the OMS system, dispatch work orders and corresponding incident tickets to the application servers. On its turn, FSMS server send order status back to source system when mobile application signals that the task is updated.

It's noteworthy that the mobile application does not establish direct communication with external systems. Instead, it interacts with back office services as an intermediary. Anyhow, when it comes to uploading observation notes and minutes, the mobile application directly communicates with the DMS server.

## Back Office

Beside logic related to task processing on mobile application, FSMS servers host an web application for system administration accessible at URL `https://fsms.eonsn.ro/G4/servlet/PortalStart`. This application is known as _Back Office_ and is used by three different actors:
- __business analyst__ for miscellaneous business rules related, for example, to tasks creation,
- __coordination center dispatcher__ for field team management and task assignment via a Gantt chart,
- FSMS __support team__ mainly for user management, system maintenance and troubleshoting.

## Tablets Networking

Tablets are equipped with mobile data provided by a third-party service. Additionally, each tablet maintains a continuous VPN connection to the on-premises private network.

Every tablet is assigned a distinct serial number, which serves as its hostname. When combined with the corporate domain, it forms a Fully Qualified Domain Name (FQDN), such as `90000724235.eonsn.ro`. This FQDN can be employed to establish a connection with the tablet using its serial number. To illustrate this, we can verify connectivity by executing a ping command from a computer within the same private network as the tablet's serial number.

```sh
$ ping 90000724235.eonsn.ro

Pinging 90000724235.eonsn.ro [10.138.53.107] with 32 bytes of data:
Reply from 10.138.53.107: bytes=32 time=360ms TTL=251
...
```

Furthermore, from a Windows system connected to the on-premises private network, we can create networking mappings and browse files system from a tablet. This is possible because tablets file system is shared.

![Tablet Network Mapping](tablet-networking-mapping.png)

# Backend Servers

Backend servers, also referred to as back office servers, are not accessible to the public via the internet. Instead, they are privately hosted within the SN network. The infrastructure comprises three environments - production, testing, and development - all designed with similar architectural configurations.

As depicted in the [FSMS Overview](#fsms-overview), every environment is equipped with a dual setup of load balancers configured for high availability (HA). Additionally, there are two application servers and two database servers in each environment. One database server is dedicated to handling real-time tasks, while the second one serves the purposes of archiving and reporting. It is important to note that the development environment deviates from this pattern by not including load balancers.

## Production Environment

The production environment plays a critical role in the FSMS system, actively participating in task processing. Is needless to say that it must operate continuously without any disruptions and is under constant monitoring by maintenance personnel.

| Host Name            | IP Address    | CPU | MEM | DISK | Function |
|----------------------|---------------|-----|-----|------|----------|
| snfsmsl10.eonsn.ro   | 10.138.95.142 | 2   | 4GB | 28GB | HA Load Balancer #1 |
| snfsmsl11.eonsn.ro   | 10.138.95.143 | 2   | 4GB | 28GB | HA Load Balancer #2 |
| snfsmsl24.eonsn.ro   | 10.138.95.132 | 16  | 125GB | 163GB | Application Server #1 |
| snfsmsl25.eonsn.ro   | 10.138.95.133 | 16  | 125GB | 163GB | Application Server #2 |
| snfsmsl26.eonsn.ro   | 10.138.95.131 | 24  | 283GB | 154GB | Work Database |
| snfsmsl27.eonsn.ro   | 10.138.95.134 | 16  | 125GB | 54GB | Archiving / Reporting Database |

## Test Environment

The test environment, also referred to as UAT, serves as the platform used by the back office team to validate mobile application packages before their deployment to production. Although this environment primarily serves testing purposes, it holds a critical role in ensuring continuous delivery and must be maintained in an operational state and regularly updated.

It's important to emphasize that the test environment should closely mirror the production environment to ensure accurate testing and validation.

| Host Name            | IP Address    | CPU | MEM | DISK | Function |
|----------------------|---------------|-----|-----|------|----------|
| snfsmsl12.eonsn.ro   | 10.138.95.144 | 1   | 2GB | 28GB | HA Load Balancer #1 |
| snfsmsl13.eonsn.ro   | 10.138.95.145 | 1   | 2GB | 28GB | HA Load Balancer #2 |
| snfsmsl14.eonsn.ro   | 10.138.95.146 | 4   | 31GB | 54GB | Application Server #1 |
| snfsmsl15.eonsn.ro   | 10.138.95.147 | 4   | 31GB | 54GB | Application Server #2 |
| snfsmsl16.eonsn.ro   | 10.138.95.136 | 4   | 62GB | 54GB | Work Database |
| snfsmsl17.eonsn.ro   | 10.138.95.139 | 4   | 62GB | 65GB | Archiving / Reporting Database |

## Development Environment

The development environment is exclusively utilized by the development team and does not play a direct role in the production pipeline. It is not mission-critical to maintain continuous uptime therefore it can be periodically stopped and started as needed. Furthermore, it does not necessitate an exact replication of the production environment and demands fewer hardware resources.

| Host Name            | IP Address    | CPU | MEM | DISK | Function |
|----------------------|---------------|-----|-----|------|----------|
| snfsmsl20.eonsn.ro   | 10.138.95.153 | 4   | 31GB | 54GB | Application Server #1 |
| snfsmsl21.eonsn.ro   | 10.138.95.154 | 4   | 31GB | 54GB | Application Server #2 |
| snfsmsl19.eonsn.ro   | 10.138.95.152 | 4   | 62GB | 54GB | Work database |
| snfsmsl22.eonsn.ro   | 10.138.95.155 | 4   | 62GB | 54GB | Archiving / Reporting Database |

## Auxiliary Servers

| Host Name            | IP Address    | CPU | MEM | DISK | Function |
|----------------------|---------------|-----|-----|------|----------|
| snfsmsl05.eonsn.ro   | 10.138.95.135 | 16  | 62GB | 206GB | FME Server |
| snfsmsm01.eonsn.ro   | 19.138.95.151 | 4   | 16GB | 100GB | FME Development Server |
| mdmadmin.eonsn.ro    | 10.138.55.135 | 8   | 8GB | 1.5TB | MDM Administrative Tasks |
| snmdmsl01.eonsn.ro   | 10.138.55.130 | 4   | 8GB | 210GB | Graylog Server |

# Mobile Application

The FSMS mobile application assists field operators in running task flows while updating the task status. A flow is a sequence of steps displayed on user interface in a way similar to a slide show presentation but interactively. The order of these flow steps may dynamically change based on the selections made by the operator.

Mobile application uses JavaFX technology and is running on Windows-based tablets. These tablets are equipped with mobile data capabilities, but the application is designed to ensure operation in offline mode as well. To enable this capability, the mobile application integrates an embedded H2 database. Initially, user database data is retrieved from servers and remains synchronized while the tablet is connected online. In offline mode, field operators can execute task flows, with task status updates being stored locally in the embedded database.

Given that tablets are connected to mobile data supplied by a third-party provider while the servers are privately hosted on-premises, a continuous VPN connection is established to bridge the gap.

The mobile application exclusively interacts with the back office application servers. This remains consistent even when the mobile application needs to transmit notifications to external systems such as SAP and OMS. The sole exception to this rule is for observation notes and minutes, which are directly uploaded to the DMS server.

## Tasks List

On mobile application there is a time service that updates periodically the tasks list from tablet. It uses `GetActions_Mobile_1.05` endpoint to retrieve team's actions list from FSMS server then convert actions into tasks.

Tasks order, based on actions order from server, determines the path team should take to travel from a task location to the next. The logic on the server side is responsible for arranging actions, and consequently the tasks within the mobile application, in a manner that minimizes travel time.

![Tasks List](tasks-list.small.png)

Only one task is active at a given moment, and only active task has a running flow. Once the task started, its flow should be executed step by step till task end. While flow is executed task status is updated. Here are task status values used by mobile application:

| FFA Code | Description |
|----------|-------------|
| A102     | Blocked |
| A171     | Assigned |
| ENRT     | On the Move |
| AWIP     | On Working |
| A501     | Closed - Solved |
| A502     | Closed - Not Solved |

FFA code is the action code as defined by server side logic. In fact, on server are way much more status codes but mobile application used only a subset.

## Task Flow
There is a significant number of task types, grouped into processes specific to the two divisions: natural gas and electricity. Task classification is managed by SAP. Given the volume, it’s reasonable to expect diversity in tasks; however, we can outline an abstract - generic and perhaps oversimplified - task flow, as shown in the diagram below.

Before executing a task, a field operator must prepare and travel to the equipment location. This justifies the first step in the diagram: prerequisite.

![Task Flow Abstraction](task-flow.png)

Upon arrival, the operator inspects the equipment to determine if conditions allow task execution. If they do, the task is performed, and SAP update forms are completed. If execution isn’t possible, the operator fills the finding' notes.

## Default Flow

When the mobile application generates tasks based on the actions loaded from the server, it utilizes an algorithm to assign a specific flow to each task. This assignment is typically determined by certain criteria, frequently the action type ID. For instance, in the case of an action with the type ID _E9DB_ and the action name _Debransare_, the corresponding flow is denoted as _EA9_Debransare_ and is retrieved from the Java resource file `/assistant/flows/EA9_Debransare.afd`.

Nevertheless, for straightforward tasks, it is not unusual to designate a default flow. This default flow encompasses the most generic steps, including initiating the flow, traveling to the task location, arriving, executing, and ultimately closing the task. It is defined by Java resource file `/assistant/flows/DefaultFlow.afd`.

Next follows the default flow steps.

### Start Task

The initial step in the default flow is, as expected, to start the task - see Task Flows Start picture. This action results in a change of the task status, transitioning it from __assigned__ to __on the move__.

![Task Flows Start](task-flows-start.xsmall.png)

### Arrive to Task Location

Upon reaching the task location, the field operator is required to notify the system. To achieve this, the operator utilizes the following flow step - picture Task Flows Arrive, which facilitates the transition of the task status from __on the move__ to __on working__.

![Task Flows Arrive](task-flows-arrived.xsmall.png)

### Work on Task

Upon completing a task, the field operator is required to specify the outcome: whether the task is considered resolved or unresolved. 

In the default flow, the subsequent step involves selecting the task resolution. This selection will then determine whether the task status is marked as __solved__ or __not solved__, depending entirely on the choice made by the operator. The responsibility for making the correct choice rests with the field operator.

![Task Flows Close](task-flows-close.xsmall.png)

### Close the Task

Following the completion of the task, the flow is terminated, and the field operator is left with only one option: to navigate to the task list. It's worth noting that the task color is changed from blue to green, indicating the task's completion.

![Task Flows End](task-flows-end.xsmall.png)

### Finite State Automaton

Here are summarized default flow steps, in a representation resembling a finite state automaton. Circles are task status whereas rectangles are task status events.

![Default Flow Automaton](default-flow-automaton.png)

For completenes here are the event codes:

| Event   | Description |
|---------|-------------|
| ENROUT  | Start moving to task location |
| ARRIVE  | Arrived to task location and start working  |
| CLSFIX  | Task is solved |
| CLSNFX  | Task is not solved |

# Glossary

| Term     | Definition |
|----------|------------|
| DMS      | Document Management System |
| DSL      | Domain Specific Language |
| ERP      | Enterprise Resource Planning |
| ETL      | Extract, Transform, Load |
| FFA      | Field Force Automation |
| FME      | [Feature Manipulation Engine](https://fme.safe.com/platform/) |
| FQDN     | Fully Qualified Domain Name |
| FSMS     | Field Service Management System |
| HA       | High Availability |
| HTTP     | Hypertext Transfer Protocol |
| OMS      | Outage Management System |
| SAP      | Systems, Applications, and Products in Data Processing |
| SAP DM   | SAP Device Management |
| SAP IS-U | Industry-Specific Solution for the Utilities Industry |
| SN       | Special Network |
| SOAP     | Simple Object Access Protocol |
| UAT      | User Acceptance Testing |
| VPN      | Virtual Private Network |
| whoami   | System application that return currently logged in user |

