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

