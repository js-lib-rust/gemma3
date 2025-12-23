---
company.name: DelGaz Grid
company.logotype: Internal use document
document.title: Mobile App Refactoring
document.subtitle: FSMS Mobile
document.version: 1.0
document.abstract: Options to improve code quality on FSMS mobile application.
document.author: Iulian Rotaru
document.date: May 27, 2025
---
# Mobile App Refactoring
Analysis of the options we have to improve code quality on FSMS Mobile App. This document starts from assumption that we have a problem with current codebase that makes development ridiculously hardy and impacts the speed and qualify of delivery. 

## Concepts
Before continuing let's agree on terms. In this document, code refactoring is understood as restructuring of the existing software code without altering its external behavior. 

The primary goal is to improve:
- readability: making the code easier to understand and maintain,
- scalability: ensuring the codebase can accommodate future growth,
- performance: optimizing efficiency without changing functionality,
- maintainability: reducing accumulated code issues and simplifying debugging,
- modularity: breaking down complex code into reusable, well-organized components.

Refactoring does not introduce new features or fix bugs directly; instead, it enhances the internal structure to facilitate easier modifications, reduce risks, and improve long-term development efficiency.

## Key Principles:
- behavior preservation: the software’s functionality remains unchanged after refactoring,
- incremental changes: small, controlled modifications to avoid disruptions,
- automated testing: reliance on tests to ensure no regressions are introduced,
- continuous improvement: regularly refining code as part of the development cycle.

# Technology
The technology currently used by the mobile application and identified weak points.

## Current Technology
The mobile application is written using Java EE, and the user interface is developed using the JavaFX platform. We should mention from the very beginning that the chosen technology made sense a decade ago, but is now considered _outdated_, so to speak.

In the meantime, Java EE has actually removed out of the Java language for many years. In Java 9, Java EE becomes deprecated, and in Java 11 it was removed. The Java EE code has been donated to the Eclipse Foundation, but it is still actively maintained. It is hard to say how popular or relevant Java EE is nowadays, considering that most developers use Spring Boot.

JavaFX was also part of the Java ecosystem, but since Java 9 it has been removed; the FSMS mobile app uses JavaFX 8. It is currently an open-source project, still maintained, but I am not sure how active the community is. What I can say is that upgrading from JavaFX 8 to 21 didn't result in any noticeable performance improvements at runtime, and in terms of styles and web support, there wasn't much to see. For example, Google Maps still doesn't work on JavaFX 21.

It's also worth noting that while JavaFX claims to cover mobile devices, it's actually designed for the desktop experience. It's certainly not designed primarily for mobile devices.

## Identified Weak Points
While Java is still relevant for backend, including cloud development, it has lost the battle to web browsers and mobile devices. A notable exception is Android devices that still use Java, although there is an ongoing migration process to Kotlin - a language similar to Java, but with improved support for the functional paradigm and dynamic types.

In any case, it is difficult to say how relevant Java EE technology is today. My personal opinion is that it is maintained by the Jakarta EE platform for backward support. There is still a large business running on Java EE.

But we must be aware that similar services to Java EE are also provided by Spring Boot, which is the current norm in Java development, although Spring applications are not 100% source code compatible with Java EE.

As for JavaFX, although the platform itself is capable of developing truly impressive desktop interfaces, we can safely say that it is not the best option for mobile development. It doesn't seem to have a particularly active community, and its market share is less than 1%. We live in a world dominated by web technologies.

But ultimately, the quality of code and application is more influenced by the developer than the technology used. Human quality is still relevant in software development. And the main disadvantage of the technologies used by the Mobile App - Java EE and JavaFX - is their lack of popularity among developers. 

## Conclusion and Recommendations
Given the declining adoption and inherent limitations of Java EE and JavaFX, we should move to modern, well-supported alternatives that align with current industry standards and developer ecosystems.

For business and persistence logic development, Spring Boot remains the dominant framework in the Java ecosystem, offering better community support, modularity, and ease of use compared to Java EE.

For frontend and mobile development, web technologies (HTML, CSS, JavaScript) and cross-platform frameworks (React Native, Flutter) offer broader compatibility and a more active developer community than JavaFX.

Adopting these alternatives will improve long-term maintainability, scalability, and developer productivity, while protecting applications from technological obsolescence.

# Architecture
This section describes the system architecture and analyzes design and implementation flaws, including business analysts' decisions impact, and suggests options to overcome them and overall steps to follow.

## Current Architecture
Current FSMS system as a whole is monolithic and monochrome using Java EE - _Java Enterprise Edition_ technologies. It is a standard, old school architecture still useable for small to medium and start-up projects. I deemed the architecture as _monochrome_ because is based on a single technology.

At highest abstraction level, FSMS is in charge with SAP work orders and OMS tickets processing. There are two major functional subsystems:
- backoffice for administrative functions and, tasks creation and dispatching to field teams,
- Mobile App used by field operators to actually fulfill the tasks.

Regarding deployment there are two major component types: server and tablet. In real deployment there are multiple environments, servers and tablets but here we discuss a HLD presentation.

![Current FSMS Architecture](current-fsms-architecture.png)

Backoffice subsystem uses three tiers architecture, well known in the Java EE world:
- presentation layer for user interface,
- business layer for logic processing,
- persistence layer for data storage into database.

Mobile App is client-server using SOAP web services for messages communication. The codebase of the server side of the Mobile App is common with backoffice, for which reason talking about _mobile's server side_ is an academic endeavor but still correct from functional perspective. 

Anyway, client part has its own distinct code base. From now on, when we discuss about Mobile App, we refer to the client part. In this document scope is only the client part, that is, the Mobile App.

Finally, it can be seen that all three tiers from the backoffice, and the server logic in the Mobile App, are on the same implementation component. All functions are on the same code base and in order to avoid deploying a single large archive, Globema uses patches. This is why the architecture is considered _monolithic_.

### Current codebase
Currently, we are using the source codebase inherited from Globema, exactly as it was. It is a kind of Maven module-based project, but with an unusual filesystem structure. The main programming language is Java, but there are also mixed C# projects and event installation kits. There are also experimental projects not finalized in any product.

| Module | Description |
|--------|-------------|
| AfdFileEditor | Experimental editor for AFD files, not finalized |
| ANT | Java parent project for Mobile App |
| API | Java business logic, persistence and common utilities |
| BatteryChecker | C# project for battery measurements |
| GeoChecker | C# project for reading tablet location |
| GUI-JavaFX | JavaFX GUI for Mobile App |
| Installer | Repository for binaries included in the build |
| Launcher | Installation kit for unknown launch application |
| UpdateInstaller | Skeleton project for installed update server |
| UpdateServer | Experimental update archives, not used in production |
| WebCam | Webcam installation kit |

It can be seen that the actual Java code for the Mobile App is present in only three directories. It is also worth noting that files that are not directly related to Java projects and can be removed, amount to about 10% of the total codebase.

### Current Design
The Mobile App design is, well, not a very much design; it is composed of only two modules:
- API: business logic, persistence, and common utilities,
- GUI-JavaFX: user interface components, mainly flows and forms.

![Current Modules](current-modules.png)

Here is a simplified overview of the services implemented by these modules. Let's start with the API modules:

| Service | Description |
|---------------|------------|
| Alerts | Manages alert listeners and notifies alerts |
| Axis2 | SOAP stub sources generated by the Maven plugin |
| Battery | Periodically reads battery status and publishes to the event bus |
| Camera | Camera interface and user-defined enumeration constants |
| Core | Context and core configuration, handler and exception logging |
| CRUD | ORMLite-based persistence services |
| Data source | Data sources for both online and offline mode |
| DMS | Create HTML documents and send them to the DMS server |
| EON | Delgaz specific ERP documents, grouped by source system |
| Event bus | Broker for recording and publishing events |
| GIS | Integration with external GIS server |
| Location | Periodic reading of geolocation and saving to local database |
| Loggers | Log management for files and records in the database |
| Materials | CRUD operations in the local database for inventory objects |
| Message | Retrieve and send messages to the local database and forced synchronization |
| Model | Model objects (entities) with ORMLite annotations |
| Snapshot | Snapshot representation for various views and forms |
| Synchronization | Periodic execution of synchronization services |
| Update | Mobile auto-update from update server, unused as far as I can tell |

And here is the GUI-JavaFX module:

| Service | Description |
|---------------|------------|
| Alert tab | Tab for system alerts |
| Assistant | Views for displaying work flow steps |
| Equipment tab | Inventory for materials, seals, SMS cards, etc. |
| General tab | Generic tab for observation notes and minutes |
| Login screen | Home page where the initial synchronization takes place |
| Main screen | Main screen layout |
| Messages tab | Messages to and from other field operators |
| Popup | Dialogs and popup forms, probably related to the General tab |
| Tasks tab | Displays the task list, active task flows, map and printing |
| Team tab | Current team members and assigned vehicle |
| Utilities | Video Camera Support |

## Design Flaws
The overall source code design decisions that are considered detrimental to code maintainability.

### SOAP Client
While SOAP is a natural choice in a Java EE architecture, it is debatable how useful it is for a mobile application. It is simply too heavy.

One could argue that there is an advantage to stub classes generated by development tools. I agree with that; but it has been proven that the generated classes cannot be used directly by the user interface and persistence logic.

![SOAP Processing](soap-processing.png)

To overcome this, Globema decided to create intermediate model classes and convert the stub classes to model based on the received message and back to stub when sending the response. It is true that the conversion logic is simple, but it requires a lot of code to write, as SOAP structures tend to be quite large: there is a document structure with over 600 fields!

Ultimately, SOAP, in our case, leads to much more code to maintain and increases resource usage at runtime, all of them: processor, memory and database storage.

### Task Loading
While FFA tasks are an exception, all other tasks created for SAP work orders and OMS tickets have an associated service order. These tasks cannot be processed without the attached orders, but the synchronization logic uses a two-step approach:
1. all task lists are loaded, but not the attached order,
2. a delayed synchronization loop is executed to load the service orders, one by one.

The end result is that the initial load time of the tasks is greatly increased for no apparent reason. The server load is also increased because instead of a single load request for the tasks, there is only one, plus the number of service orders.

I was tempted to think that the tasks are loaded without orders to speed up the initial display of the task list; but I discovered that in fact the task is only displayed in the task list after the attached order is loaded.

Then I thought that it could be because of the task status updates. Theoretically, this could be the case, but nothing prevents us from declaring the service order as optional and sending it null or not sending it at all on task updates.

In case we are concerned about the increased size of the task list plus the attached service order: keep in mind that dictionaries and sometimes serials exceed 16 MB of XML. A task XML is on average 4 KB and a service order somewhere around 6-8 KB, for a total of, say, 12 KB. We need more than 1000 tasks and attached orders to reach the size of the dictionaries or the large serials list.

The main disadvantages of the current task loading logic are:
- slow loading times, which become especially problematic with a large number of tasks,
- higher network bandwidth consumption due to inefficient data loading,
- increased server load, as multiple requests are required instead of a single optimized one.

### Periodic Requests
To keep the Mobile App tasks up to date, there is a periodic check for new task assignments or task status changes (e.g. a task canceled by the dispatcher), which is clearly suboptimal. If we look at the distribution of SOAP requests across endpoints, from the mobile app to the Backoffice server, we can see that almost half (41%, to be exact) are for tasks.

![GetActions Requests Share](get-actions-requests-share.png)

Of course, this means a waste of network bandwidth, probably paid for, and tablet processing power, affecting battery life and user interface response times. Also, for performance reasons, periodic checks cannot be performed very often, which leads to delays in tablet updates; this delay is particularly critical for OMS tasks.

The same periodic verification model is applied to other resources like materials, messages, alerts, etc., but the impact is not as great as in the case of tasks.

To conclude, here are listed the identified inefficiencies:
- network bandwidth waste: the frequent polling of task updates consumes unnecessary data, increasing operational costs,
- battery drain: continuous background requests strain the tablet’s battery life, reducing the device’s operational time and requiring more frequent recharging,
- delayed updates: since polling cannot be performed too frequently without degrading performance, there is an inherent lag in receiving critical updates. This delay is particularly problematic for OMS tasks, where real-time synchronization is crucial,
- server load: the high volume of periodic requests places unnecessary load on the Backoffice server, potentially slowing down responses for other operations and increasing infrastructure costs,
- user experience impact: processing frequent background checks can lead to occasional UI freezes or sluggishness, negatively affecting the responsiveness of the Mobile App,
- inefficient resource use: even when no updates are available, the system repeatedly checks for changes, wasting both client and server resources.

### Using Sync for Async
Here is a design I have never seen before, and it is hard to find a reason why the author comes up with such a complicated solution. In short, it is about using the synchronization mechanism for asynchronous server calls instead of callbacks or Java Futures, both present in Java 8.

The easiest way to explain is to exemplify with a code example. Note that the code example is greatly simplified, reduced to what is strictly necessary for the explanation. Also, the core of the synchronization service is not shown, but we should keep in mind that it exists.

There is a synchronization service for the cars assignment operation. This is used when the user taps the button to update machines in the team tab. Here is the service declaration.

```java
enum Service {
    CAR_ASSIGNMENT_SYNC("CarAssignmentSync", (core) -> {
        SyncService syncSrv = new SyncService(core.getConfig(), core.getOfflineDataSource(), core.getOnlineDataSource());
        syncSrv.addOperation(new SendCarAssignmentRequest());
        return syncSrv;
      })
}
```

In the class responsible for the team tab, the service is created and stored it locally in the `syncService` field. Then we add a listener called `carSynchronizationListener` that updates the user interface after the car assignment synchronization is performed. The request to the backoffice is initiated by the `updateVehicleButtonAction` handler when the user presses the update button. We go through a few steps here, but in the end the static method `FfaDataSender.sendCarAssignmentRequest` is invoked, which creates a SOAP request and sends it to the backoffice.

```java
class TeamTab {
    SyncService syncService;

    void initServices() {
        syncService = EonAntCore.getService(EonCoreFactory.Service.CAR_ASSIGNMENT_SYNC.id);
        syncService.addSyncListener(carSynchronizationListener);
    }

    Consumer<SyncLogEntry> carSynchronizationListener = entry -> {
        PlatformTools.runInFxThread(this::refreshAssets);
    };

    void updateVehicleButtonAction(ActionEvent actionEvent) {
        sendSelectedVehicle(principalVehicle, secondaryVehicles);
    }

    void sendSelectedVehicle(TeamVehicle principalVehicle, Set<TeamVehicle> secondaryVehicles) {
        new Thread(() -> { syncService.sync(); }).start();
    }
}
```

I will anticipate and present a refactored solution here. First, we create a new interface responsible for invoking the server API, let's call it `IServerApi`.

```java
interface IServerApi {
    void sendCarAssignmentRequest(String crewID, String[] carID, Runner callback);
}
```

In the cars update management button, we solve the whole problem in one line: invoke the API service with a callback.

```java
class TeamTab {
    @Autowired
    IServerApi serverApi;

    void updateVehicleButtonAction(ActionEvent actionEvent) {
        serverApi.sendSelectedVehicle(principalVehicle, secondaryVehicles, () -> { 
            PlatformTools.runInFxThread(this::refreshAssets); 
        });
    }
}
```

Finally, keep in mind this example is not the only case.

Drawbacks of this approach:
-  unnecessary complexity: using a synchronization service for a simple async operation introduces layers of indirection (listeners, thread management) that could be replaced with a straightforward callback,
- tight coupling with sync mechanism: the UI logic is now dependent on a synchronization framework, making it harder to modify or replace the underlying async mechanism,
- manual thread management: spawning a new thread is error-prone and less efficient than using built-in async constructs like CompletableFuture,
- obscured error handling: errors in the sync process may not be properly propagated to the UI, whereas a callback-based approach can include explicit error handling,
- performance overhead: the sync service likely includes additional logic that is unnecessary for a simple async request, adding latency,
- harder to test: mocking the SyncService and its behavior is more complex than mocking a simple async interface.

### Do We Really Need SQL DB?
The question is not whether our Mobile App needs local storage, because it obviously does for offline work. It is about the relational database, also known as SQL database.

As the name suggests, relational databases should be used where there are relationships between tables. A good indicator of the presence of relationships are SQL queries that use JOINs between multiple tables. From what I have observed so far, there are no JOIN queries in the application codebase. Or there are so few that I have missed them completely.

The common persistence logic model is to handle the entire object or even a collection of objects in a single query and use Java streams for filtering and sorting.

```java
private Stream<Task> readAllValidActiveTasks() {
    return readAllValidFinishedAndOngoingTasks().stream().filter(Task::isActive);
}

public List<Task> readAllSortedTasks() {
    return readAll().stream().sorted(taskComparator()).collect(Collectors.toList();
}
```

My guess is that we can replace the SQL database with a document database, that is optimal for our application's usage model. So, it seems the answer is that we don't need a relational database.

### External Services
There are external services like battery measurement and location detection, which are implemented as external executables and launched from a Mobile App by creating a process, external to the JVM - _Java Virtual Machine_. Communication between these external processes and Java is mediated by the operating system through standard IO streams.

![External Process](external-process.png)

In diagram is exemplified with battery measurements but for location detection is similar.

Creating an external process is expensive from a processor and memory perspective. And, what is worse, these processes are created periodically. Also, being an external process, Java has no control over its life cycle and in case the process hangs (quite plausible, since in our case it uses hardware resources), Java waits with a timeout.

### Local Logging
Issues with the current logging system:
- complex programmatic configuration of logging handlers, which makes maintenance difficult,
- reliance on Java Logging (JUL), which is widely considered an inferior solution in the industry,
- lack of a centralized logging server, which prevents log aggregation and analysis,
- lack of critical error alerts, which prevents prompt responses to fatal issues.

#### Programmatic Configuration
Logging handlers are configured programmatically in code, rather than through external configuration files (e.g. log4j2.xml or logback.xml).

Impact:
- makes it difficult to change logging behavior without code changes,
- increases the risk of misconfiguration due to manual configuration,
- reduces flexibility in adjusting logging levels at runtime.

#### Java Logging (JUL)
The system uses java.util.logging (JUL), which lacks advanced features compared to modern frameworks like Log4j 2 or SLF4J + Logback.

Impact:
- poor performance in high-throughput applications,
- limited flexibility in log formatting, filtering, and appending options,
- inconsistent with industry best practices (most companies prefer Log4j 2 or Logback).

#### No logging server
Logs are stored locally on the tablet without aggregation, making it difficult to troubleshoot related errors or perform statistical analysis.

Impact:
- no unified view of logs across tablets,
- more difficult to correlate errors that occur on multiple tablets,
- no historical retention of logs for audits or post-mortem analysis.

#### No fatal error alerts
Fatal errors are only logged, but do not trigger real-time alerts (e.g. emails, SMS).

Impact:
- delayed response to incidents due to manual log monitoring,
- increased risk of prolonged mobile application downtime.

## Implementation Flaws
This section lists known code design and implementation defects, as well as suboptimal tools and processes. All of these have an impact on the development effort and the quality of delivered artifacts.

### Automated Test Coverage
Test coverage is the percentage of the codebase that is automatically tested by unit tests, integrated into the development tools. The recommended coverage depends on how critical the application is. For our Mobile App, where we have zero tolerance for regressions, code coverage should exceed 90%. The current test coverage is about 14%.

It is clear that we need to move to TDD development - Test Driven Development. As a side effect, the quality of the code is expected to increase, since it is a well-known fact that testable code imposes good practices.

But this means that we need a developer for testing. We also need to avoid the misconception that the tester is not relevant and can be a junior. Far from the truth: the tester must understand the business requirements very well, in fact, better than the developer. The developer can rely on tests to ensure that his implementation is valid and compliant with the business requirements.

Ideally, the tester is more connected to the business analyst than to the developers. He acts as a bridge between the business and development teams.

By writing tests while the business requirements are being consolidated, the tester can help understand and uncover logical flaws in the specifications. The tester plays a critical role in ensuring the quality of the business requirements and provides test cases for all changes from the specification.

Drawbacks of low-test coverage:
- increased risk of undetected bugs: critical defects may slip into production, leading to crashes,
- higher regression risk: changes in one part of the system may unintentionally break existing functionality without automated tests catching it,
- slower development cycles: without reliable tests, developers spend more time manually verifying changes, delaying releases,
- difficulty in refactoring: low coverage makes refactoring dangerous, as there’s no safety net to ensure behavior remains correct,
- poor code quality: untested code tends to be less modular and harder to maintain,
- higher debugging costs: issues discovered late in production are exponentially more expensive to fix than those caught early by tests,
- lack of confidence in releases: deployments become risky, leading to hesitation in delivering updates or new features.

### Code Structure
As shown in the [current codebase](#current-code-base) structure, there are actually two modules in our Java code base: API and GUI-JavaFX. There is also the ANT module, the parent of the aforementioned modules, but without code or resources.

![Current Modules](current-modules.png)

Given the size of the codebase and the number and diversity of services implemented, this modularization is too weak. 

And here are some consequences:
- lack of modularity means that the code is tightly coupled, making it harder to update without breaking the entire system,
- fewer modules mean that each class contains excessive logic, forcing developers to analyze large blocks of code to understand even simple workflows,
- without modular separation, it is unclear where to start reading or how components interact,
- unstructured code forces developers to mentally trace execution paths between unrelated functions,
- large, interconnected modules make it difficult to test individual components in isolation,
- changing one part of the code can unexpectedly break other functionality.

### Code Tightly Coupling
A major problem with the current implementation is the lack of CDI - Context and Dependency Injection, also known as IOC - Inversion of Control. Although CDI is part of Java EE, on which the Mobile App is based, Globema somehow failed to include a CDI implementation.

For this reason, dependencies are explicitly created by the owning classes. Using dependency declarations at such a low-level lead to an uncontrolled dependency graph, commonly known as spaghetti code.

Drawbacks of tight coupling without CDI:
- reduced testability: without dependency injection, unit testing becomes difficult since mock objects cannot be easily injected; this leads to reliance on real implementations or cumbersome workarounds,
- harder maintenance: changes in one class often require modifications in multiple other classes due to direct instantiation of dependencies, making the codebase fragile,
- poor scalability: adding new features or swapping implementations requires extensive refactoring since dependencies are hardcoded rather than loosely coupled,
- increased risk of bugs: manual dependency management is error-prone, as developers must ensure correct initialization orders and lifecycle management,
- difficult refactoring: without a centralized CDI container, tracking and updating dependencies across the codebase becomes tedious and risky.

### Public Implementation
A good architecture keeps dependencies controlled and clean and avoids circular dependencies. A dependency is created when a class invokes services from another class. To reduce the coupling between classes, there is the option of hiding them inside modules. Here the term _modules_ include also _packages_.

Controlling class visibility is considered so important that it has been a feature of the Java language since the beginning.

![Public Implementation](public-implementation.png)

Unfortunately, the current implementation does not use this best practice. All classes are publicly available, so they can be accessed from anywhere. This and the lack of CDI increase code coupling, make code changes difficult, and increase the chances of unexpected side effects.

Drawbacks of public implementation:
- increased coupling: since all classes are exposed, external modules can freely depend on internal implementations, making the system more rigid and harder to refactor,
- reduced encapsulation: implementation details are exposed, violating the principle of information hiding and making maintenance riskier,
- difficulty in refactoring: changes to public classes may require updates across multiple modules, increasing development effort and the chance of errors,
- higher risk of circular dependencies: without proper visibility control, unintended bidirectional dependencies can emerge, leading to design flaws,
- testing challenges: public exposure of all classes may force tests to rely on unstable implementation details rather than stable contracts provided by interfaces.

### Forms Development Cycle
This is about forms editor. The main problem we have here is that development is not WYSIWYG - _What You See Is What You Get_. Developing an user interface from code is like working blind folded and doubles the development time, to say the least. For complex forms, which seems to be the norm, development time overhead increases significantly.

Development cycle on current tools is completely inefficient: user interface layout is described in a custom XML domain specific language using an integrated text editor with some auto-complete support, build entire application and run then observe changes on real forms while running the application. One second feedback is transformed in minutes.

Now, to tell the truth, there is a JavaFX designed provided by open-source community and also integrated into development tool. It has not the best preview and is not real time but is more than nothing. Unfortunately, it is not working with our FXML files, most probably due to the custom components created by Globema.

Here is a screenshot of integrated FXML editor:

![Form Editor](fxml-editor.png)

And here a failing attempt to open the FXML designer. Error message is misleading: it suggests that we can solve the problem by installing designer but it is already installed.

![Form Designer Fail](fxml-designer-fail.png)

Please note that on separated projects, using standard components, designer is working.

### Forms as DMS Docs
There is a need to save completed forms on the DMS server in HTML format. A solution implemented by Globema is to read the form component tree from the screen and generate the HTML document, node by node. The resulting HTML document is a copy of the application form, but with weak styling.

To optimize the appearance of the DMS document, business analysts responsible for form design have started replacing standard form controls with custom solutions. For example, standard checkboxes are replaced with two buttons: _YES_ and _NO_.

There is also contextual text that does not need to be updated in the application forms, but only be present in the DMS documents. This adds complexity to form development and sometimes worsens the user experience by presenting information that is not strictly necessary for filling in the form data.

Here we have two non-overlapping needs, fulfilled by the same document format:
1. form filling by field operators: focus only on data entry and optimization for simplicity and ease of entry,
2. document analysis by business personnel: complete and contextual data, presented in a structure that facilitates understanding of relevant relationships.

For example, there are forms with a title section regarding the customer address or the location of the equipment. This information is irrelevant for the field operator, since he is already at the location; but this address information is needed in the DMS document.

In fact, all the form fields that are not updated by the field operator are, in most cases, not strictly necessary, increase complexity and waste screen space.

### Forms Custom Controls
Entire application user interface is created using custom GUI components inherited from Globema. These components are complex with many ways to solve the same the same problem and not documented at all. While they offer some services there is a great deal of effort to understand them and to use them correctly.

There is also a lack of consistency on these components; it is like they were developed without supervision: every developer when needed some functionality added there even it was already implemented in some obscure ways.

```xml
<PropertyField modelKey="preparedBy" fx:id="preparedBy" initialValueKey="context#preparedBy" labelText="%issued_by" labelWidth="485" type="INPUT_ENABLED" fieldWidth="600" GridPane.rowIndex="0" GridPane.columnIndex="0" styleClass="property-field-size" saveType="TO_MODEL" saveOnFocusLost="true" />
```

Being custom components there is no community where developer can ask for help, not even using latest AI based tools, and we cannot expect to find developers to know them.

To be correct there is nothing wrong on custom components provided they are written and documented well, which is not the case.

### Fixed-position layout
FXML is a domain-specific XML language created by JavaFX to describe user interfaces.

We are faced with an anti-pattern used in most FXML descriptors: fixed positions and dimensions of components, in pixels. This inevitably leads to the impossibility of scaling to different screen sizes, and we can consider ourselves lucky that we only have two formats - in the real world of mobile devices there are dozens.

This is the main reason why we have two development branches.

Also, maintaining a fixed layout is more difficult. There is a considerable development effort to try to convince a component to have the correct size and place.

The correct way to describe a user interface is to use flexible and fluid layouts. FXML descriptors should only define the structure, not try to control the exact position of components on the screen. It is the responsibility of a layout manager to calculate absolute dimensions and position on the screen using pixels. This way, the user interface automatically scales to different screen sizes and resolutions.

A simple example: the grid layout. In this case, the position of the components is controlled by indices on two axes: horizontal and vertical. If we want to add a component somewhere at the top of the grid, we have to manually update the indices of all components!

A real example from the codebase. Please note _GridPane.rowIndex_ and _GridPane.columnIndex_ attributes.

```xml
<Pane GridPane.rowIndex="0" GridPane.columnIndex="1" GridPane.columnSpan="2" GridPane.halignment="CENTER" styleClass="grid-field-pane">
        <Label text="%metter_dismount" styleClass="grid-field" style="-fx-padding: 0 0 0 30"/>
</Pane>
<Pane GridPane.rowIndex="1" GridPane.columnIndex="0" styleClass="grid-field-pane"></Pane>
<Pane GridPane.rowIndex="2" GridPane.columnIndex="0" styleClass="grid-field-pane">
    <Label text="%type" styleClass="grid-field"/>
</Pane>
...
<Pane GridPane.rowIndex="11" GridPane.columnIndex="0" styleClass="grid-field-pane">
    <LabelMandatory text="%counter_connection"  styleClass="grid-field"/>
</Pane>
<Pane GridPane.rowIndex="12" GridPane.columnIndex="0" styleClass="grid-field-pane">
    <LabelMandatory text="%connection_quantity" styleClass="grid-field"/>
</Pane>
```

Please note that what is described in this section is not a technological limitation, but just a misuse.

Drawbacks of fixed-position layouts:
- poor responsiveness: fixed pixel values prevent UI elements from adapting to different screen resolutions and aspect ratios, leading to cut-off or misaligned components,
- increased maintenance effort: any change in layout requires manual adjustment of all affected components, increasing the risk of errors and inconsistencies,
- brittle UI structure: adding or removing elements often forces developers to recalculate positions for all surrounding components, making the layout fragile,
- duplication of work: supporting multiple screen sizes requires maintaining separate FXML files and code branches,
- limited dynamic adjustments: fixed layouts struggle with dynamic content often requiring hardcoded overrides.

### Static Dictionaries
In the current implementation, dictionaries are stored in two places: in the Backoffice database and in the mobile application. The latter are only a few and are known as static dictionaries. To complicate matters, there are, is right only a few cases, of name collisions, where a dictionary is present in both places; however, static dictionaries take precedence.

This creates confusion when updating dictionaries and requires an additional step to figure out where to make the change.

Disadvantages of maintaining dual update logic:
- artificially increases the complexity of the mobile application codebase with logic that is not strictly necessary,
- need to maintain two different ways to update dictionaries,
- changes to static dictionaries require a new version of the application, slowing down updates compared to changes on the server,
- issues harder to track down: if a problem occurs, it is harder to determine whether it is caused by the server or local data.

### Logs in Database
While storing logs in databases is not a bad practice in itself, in our embedded relational database it might not be the best option. For logging, it is recommended to use non-relational databases (NOSQL), such as document databases, which are optimized for storing records in JSON format.

First, we have an embedded database with a single connection. This means that the application logic would have to wait while the records are stored. Logs also increase the size of the database, and for embedded databases that work with memory constraints, size matters because it affects its speed.

In addition to performance issues, storing logs in the database leads to gigantic databases. We have had tickets for unusually large databases, 60 GB in size (I'm not sure of the exact value, but it is of that order of magnitude) caused by the ANT_LOGS table.

To sum-up storing logs into embedded relational databases may lead to application performance limitation and higher resources consumption. Also make more difficult to centralize logs because in our case is not possible to access the database while is opened by application.

Key disadvantages:
- performance bottlenecks: since we use a single-connection embedded database, the application has to wait for log writes to complete, which introduces delays to critical operations,
- increased memory usage: logs significantly increase the size of the database, which is problematic for memory-constrained devices,
- database performance degradation: large embedded databases slow down the queries,
- unmanageable growth: we have encountered cases where the ANT_LOGS table bloated databases to ~60 GB,
- resource overuse: frequent log inserts increase disk I/O and memory usage, competing for limited resources.

### Building Process
Due to my limited knowledge of this topic, I prefer to list only possible flaws and limitations, with the caveat that I could be wrong. This section should be reviewed by the build process master and possibly by an external professional experienced in building continuous delivery products.

#### Build Automation
In an ideal world build should be performed automatically and notification sent to deployer. Deployer retrieve the archive and deploy it on production. This is core concept on continuous delivery and is mandatory on continuous integration. Code developer job is terminated when changes are committed on Git repository and build pipeline is started.

In our real-world build is manually.

#### Branch Merging
One step in building process is merging development branch into production branch. Ideally git server is able to do it automatically and if there are conflicts, they should be solved by developer updating development branch. 

Note that branch merging should be performed __before UAT__. In our setup merging is performed manually by cherry peeking, __after UAT__. 

This manual merging is in fact nullifying the UAT test. Any error introduced in this manual merging is susceptible to reach production. Manual merging is critical and cannot be performed by a not well-trained developer. It requires to be able to _feel_ the possible logic conflicts between development and production branches.

#### UAT Integration
Regarding UAT integration in build / deployment process there are two rules of thumb:
1. UAT is performed on the final merged code, ready for production.
2. Production branch tested on UAT is not allowed to be changed between tests and deployment.

These rules are to ensure we go live in production the tested branch and there are no changes on branch between UAT and deployment.

In current build process the branch tested by UAT is then merged manually into a production branch, see [branch merging](#branch-merging). On merged production branch there is a minimal, smoke testing, that cannot catch conflicts of logic possible to be introduced in manual merging.

### Deployment Process
We must be aware that the architecture of a software product does not only affect the quality and performance of the source code.

It also impacts the build and deployment processes: a monolithic architecture builds and deploys the entire code base every time a change is made, no matter how small.

For example, in the current implementation, the Mobile App is deployed as a single archive of about 60 MB, even if we change a single form; with a modular architecture we can reduce it to less than 1 MB, with an impact on deployment time and network traffic.

And in a continuous delivery system, deployment time matters.

## Business Impact
We focused so far on code quality, strictly from source code perspective. But the code itself is actually the business logic implemented in a programming language. If business logic is not structured is hard to keep a clean and well-structured codebase.

Unfortunately, we have a status quo established on many years of collaboration with an external service provider. Due to financial interests, service provider accepted complex and sometimes not consistent requirements even if hard to develop, that in time contributed to code quality degradation.

A code can be kept well-structured if its requirements are structured and consistent. If every required change has its own way to solve a problem, code complexity increases and structure is lost.

I am not trying to move responsibility; we need only to be aware of business requirements impact. This means that developers' team, or better an analyst from FSMS team, should have the option to negotiate and adjust requirements. In the end we are responsible for the codebase quality.

A small example on a real form: probably for better integration on HTML document for DMS, business required using two buttons instead of a standard checkbox.

![Using Buttons instead of Checkbox](buttons-vs-checkbox.png)

And here is the code we need to add to convert those two buttons into a hidden checkbox.

```javascript
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM is ready!');

    const CSS_SELECTED = 'selected';

    const conformCheckbox = document.querySelector("input[name='CORESPPE116']");
    const conformButton = document.querySelector("button[name='ppe116-conform-button']");
    const notConformButton = document.querySelector("button[name='ppe116-not-conform-button']");

    conformButton.addEventListener('click', event => {
        event.preventDefault();
        console.log('conform');
        conformCheckbox.checked = true;
        console.log(`conformCheckbox.checked: ${conformCheckbox.checked}`);
        conformButton.classList.add(CSS_SELECTED);
        notConformButton.classList.remove(CSS_SELECTED);
    });

    notConformButton.addEventListener('click', event => {
        event.preventDefault();
        console.log('not conform');
        conformCheckbox.checked = false;
        console.log(`conformCheckbox.checked: ${conformCheckbox.checked}`);
        conformButton.classList.remove(CSS_SELECTED);
        notConformButton.classList.add(CSS_SELECTED);
    });
});
```

If we can negotiate business requirements maybe we can agree to use standard checkbox and alleviate the need to write above code.

![Replace Buttons with Checkbox](buttons-vs-checkbox-fix.png)

With this simple UI change we can eliminate the above script. It can also be argued that the UI is cleaner because it uses a standard, well-known checkbox control.

# Refactoring
Monolithic architecture is old, from period where applications complexity was reasonable and still works well for small, start-up system. 

Once system complexity increases monolithic approach [limits](#faible-points) starts to mater. The current trend is to migrate to microservices or at least to broke the system in multiple modules that can be developed and deployed in isolation.

The same principles apply to Mobile App too but considering those 60-80 KLOC (Kilo Line Of Code) there is not a so much pressure to use micro-services; it is enough to use the right granularity in code modularization.

## FSMS Windows Service
The basic idea is to create a Windows service, probably called FSMS Service, and move some services from the mobile application there. In addition to the service-specific logic, such as battery measurement and location detection, the FSMS Service should have a REST controller and local memory. The mobile application can use a standard REST client to communicate with the FSMS Service.

The FSMS Service lifecycle is managed by the operating system: it is automatically started and gracefully shuts down before the operating system shuts down. This way, the FSMS Service is guaranteed to always run, regardless of whether the mobile application is open or closed.

![FSMS Service](fsms-service.png)

From the very beginning, the FSMS Service will have two services: battery measurement and location detection. These services will be executed periodically, and the values ​​will be saved in local memory - see [External Services](#external-services-1) for migrating the battery and location services. Note that in the current implementation, location is only monitored if the Mobile App is running.

The next step could be to collect logs and send them to a [centralized logging system](#tbd-centralized-logging-system) with (near) real-time notifications of fatal errors in the Mobile App, in which case an automatic restart of the Mobile App is possible.

It is also possible to prepare the tablet for a new workday by automatically starting the Mobile App and synchronizing tasks, just before the actual start of the workday.

DMS document processing can also be moved to the FSMS Service; this can solve a limitation of the current Mobile App design related to the impossibility of synchronizing DMS documents if the user does not log in. GIS integration is another service that can be moved from the Mobile App to the FSMS Service. Also, private keys for meter readings, and so on... The idea is to move all services that are not strictly related to processing flows and forms out of the Mobile App.

Key Benefits:
- improved reliability: since the service runs independently of the Mobile App, critical functions continue working even if the app crashes or is closed,
- resource efficiency: offloading background tasks to the service reduces the mobile app’s memory and CPU usage, improving overall performance,
- always-on functionality: essential services remain active 24/7 without requiring user interaction,
- simplified maintenance: centralizing services in a single component makes updates and debugging easier,
- enhanced security: sensitive operations (e.g., private key management) can be isolated in a more secure environment,
- automated workflows: enables features like pre-dawn task synchronization and automatic app restarts in case of fatal errors.

## REST Server
To overcome the disadvantages of [SOAP Client](#soap-client), we simply need to replace it with the REST protocol using JSON payload. REST is a lightweight protocol and is the norm in today's data communication, scalable from mobile apps to huge micro-services in the cloud.

![SOAP Processing Fix](soap-processing-fix.png)

The JSON format is so relaxed - compared to SOAP, which is more strictly typed - that it can be directly parsed and serialized from the internal models of the Mobile App. No additional conversion steps are required. But this comes at a cost: we need to add a REST server on the FSMS infrastructure and convert the REST protocol to SOAP which remains in use by the backoffice logic.

![REST Server](rest-server.png)

In any case, the proposed new REST server is needed anyway, as it acts as an API gateway that allows us to direct specific requests to different servers like DMS and reporting, while preserving SOAP communication with the existing backoffice. 

More, REST server supports push via JAX-RS SSE API. This may allow us to replace periodic requests from Mobile App to backoffice with events pushed in real time from server to tablets, of course provided that tablet has networking active.

Here are some benefits of using the REST server:
- single entry point for all API requests, reducing complexity for the Mobile App,
- converts costly periodic server polling with real-time server push notifications,
- facilitates refactoring in small increments by routing to the new servers gradually, when they become available,
- enables gradual rollouts (canary releases) to test new features safely,
- tracks API usage, performance metrics, and error rates.

If there are concerns about the processing delay introduced by the REST server, it is worth noting that all cloud service providers use API gateways, which is a well-established design pattern when working with containers.

In terms of REST server performance, there is an open-source production-grade server, a reference implementation of the Java JAX-RS API. It is similar in usage to Spring's REST controller.

## Code Structure
This section contains options to overcome code structure flaws.

First thing first: modules granularity. For me is obvious - see below Modules Granularity diagram - that we need to increase the number of modules. Choosing the right modules granularity helps in:
- controlling dependencies between modules in Java 9 makes it easier to keep them clean,
- internal implementation details are hidden, exposing only necessary interfaces - see below discussion about public implementation fix,
- changes in one module have minimal impact on others if interfaces are well-defined,
- developer can focus on one module at a time without needing to understand the entire codebase,
- developer can work on different modules simultaneously without conflicts.

![Modules Granularity](modules-granularity.png)

With codebase modularization we may need also to adjust the build and deployment policy. For example, even if we have multiple code modules, we can still build and deploy a single archive; or we can create libraries for each module.

Although this modularization should be agreed upon by all developers, I can suggest creating a separate library for common utility functions. This library, perhaps called fsms-commons.jar, should be stored in DevOps and added as a dependency to the mobile application project.

We may also need to move out services that are not strictly related to the functionality of the Mobile App. Services candidates for moving out are battery measurement and location detection - see [external services fix](#external-services-1), DMS - see [server side DMS](#tbd-server-side-dms-docs) and GIS - probably to be integrated into [FSMS Service](#tbd-windows-fsms-service). 

Regarding [tight coupling](#code-tightly-coupling), we have two options:
- refactoring the code for the Spring framework which has dependency injection, called IOC in Spring jargon,
- using the lightweight Google Guide library.

Both options provide similar services in terms of dependency injection. Ultimately, the choice is a matter of developer taste. I would vote for Spring, as it is much more popular.

Now, a solution for [public implementation flaw](#public-implementation); in order to keep dependencies controlled we need to expose outside modules or packages only what is strictly necessary.

If you do not believe me here is a well-known saying:
>Do not let your left hand know what your right hand is doing.

To do this, it is desirable to hide implementation details inside modules or packages and expose only what is strictly necessary. It is also considered good practice to expose interfaces and make implementing classes private in the package. 

![Public Implementation Fix](public-implementation-fix.png)

In this way, the amount of visible code is greatly reduced, as is the number of possible connections between pieces of code. Also, because the developer knows for sure that a class is not used outside its package, he is free to make changes to the implementing classes without worrying about breaking code in other packages.

Because each module exposes only a limited set of well-defined interfaces, the system as a whole becomes much easier to understand. Implementation details remain hidden, making it easier to understand individual modules, while design and documentation efforts can focus primarily on the interfaces. Interfaces are optimized for clarity and ease of use, while implementation classes are optimized for correctness and performance.

Of course, this private package protection does not work for Java reflection. However, since Java 9, modules allow reflection to be enabled only for the desired classes or to be completely disabled.

## HTML Forms
Here's how we can overcome the issues related to forms: switching to HTML documents. Let's start with the benefits, then we'll describe some details about the suggested implementation.

### Web Technologies vs JavaFX
Benefits of using web technologies to implement the forms:
- richer styling: CSS in HTML5 offers more advanced styling options than JavaFX CSS,
- responsive design: it's easier to create layouts that adapt to different screen sizes; no more two production branches,
- live preview: there are a lot of options; currently, I use the Live Server extension for Visual Code
- web APIs: direct access to geolocation, camera, microphone, and other browser APIs,
- better tools: advanced debugging tools in browsers, better IDE support,
- larger developer base: more developers know HTML/JS than JavaFX,
- active ecosystem: access to thousands of open-source libraries and frameworks,

Here is a side-by-side features comparison:

| Feature | JavaFX/FXML | Web Technologies |
|---------|-------------|------------------|
| Preview Latency | Minutes (mobile app rebuild and run) | Milliseconds |
| Style Editing | Limited CSS Support | Full CSS3 with Visual Tools |
| Preserving Form Values ​​| Loses Values ​​on Refresh | Can Maintain Values ​​|
| Device Testing | Requires Emulation | Real Devices via Browser Sync |

### Forms Development
Developing process is designed for gradual forms migration. It supports existing FXML forms allowing creating new one using web technologies. The key ingredient that makes this smooth integration possible is the JavaFX WebView.

The core principle is simple: WebView is a standard JavaFX node that can be used everywhere an FXML node can be used, including but not limited to assistant views, that contains forms. Here is FXML form using only JavaFX nodes:

![Forms Migration - FXML](forms-migration-fxml.png)

The same assistant view but with HTML form elements integrated by JavaFX WebView node:

![Forms Migration - HTML](forms-migration-html.png)

All FXML form's control nodes are replaced with related HTML control elements. For example, FXML `TextField` and `ComboBox` are replaced into HTML form by `input`, respective `select` elements. In both cases FXML `Button` node triggers FxView saving method but on HTML form behavior is different: it usually obtains JSON object (that is an extension of a Java Map) with key values loaded from HTML form.

```java
void save() {
    JSONObject formObject = new JSONObject(new JSONTokener(getComponent().getFormData()));
    ...
}
```

Once form object retrieved from HTML form its processing is similar to FxView model.

Beside HTML file that describe the layout an HTML form has also style and JavaScript files. All files of the HTML form are stored on Java resources, under `forms` directory. 

WebView form loading is performed on FxView controller initialization.
```java
void initialize() {
    URL url = getClass().getResource("/forms/form.htm");
    webView.load(url.toExternalForm());
}
```

WebView engine loads HTML page then scan for style and script files, then load and execute them.

Key benefits:
- seamless integration: WebView is a standard JavaFX node, meaning it can be used anywhere FXML nodes are used, including assistant views and dialogs,
- gradual migration: developers can transition forms incrementally, avoiding large-scale rewrites while maintaining existing functionality,
- modern web capabilities: HTML forms enable richer UI experiences with CSS animations, responsive design, and advanced JavaScript interactivity,
- simplified data handling: HTML forms return data as JSON objects, making it easy to process and integrate with Java logic,
- consistent styling: CSS allows for centralized theming, ensuring a uniform look across both FXML and HTML forms,
- easier maintenance: separating form logic (HTML/JS) from business logic (Java) improves code organization and maintainability.

### Integrated Forms Development
Here is a proposal for an integrated process for developing forms based on HTML.

FSMS forms are developed in Code Studio with the extension for real-time preview. There is a single form document developed, then reused by all processes related to the form: in the Mobile App tasks' flow, printing forms to Zebra, and A4 DMS documents. This is possible because HTML forms have a flexible and fluid design that scales across all types of devices and media sizes.

Since HTML is a specialization of the well-known XML standard, and given that recommended tools like Visual Studio Code are both popular and user-friendly, HTML forms can be created and maintained even by non-programmers, such as business analysts. This approach requires deeper knowledge of the form structure and how controls map to SAP fields rather than expertise in HTML or the development tool itself.

![Forms Integration](forms-integration.png)

Benefits of using integrated forms development:
- no programmers required: HTML forms are developed using a small subset of HTML and does not require programmer skills,
- lightweight development tool: HTML forms can be developed with Visual Studio which is very popular and easy to use,
- no code solution: we can create an FSMS Forms Studio for graphical form development that completely hides the HTML and can be used directly by the BU,
- write once, use everywhere: a single HTML form is created, then reused in all processed forms,
- no low-screen code branch: no need to maintain two production code branches,
- improved form quality: better form appearance due to full CSS support superior to JavaFX styling,
- easier forms to use: HTML controls are much more common in daily interaction than JavaFX controls,
- improved appearance consistency: ensures uniform style and functionality across all devices and environments.

## Server Side DMS Processing
Currently, the generation and synchronization of DMS documents is done on the Mobile App, adding unnecessary complexity to the codebase and increasing the tablet's resource consumption at runtime.

![Current DMS Processing](dms-processing.png)

In conjunction with the refactored [forms development](#forms-development), we can use the same HTML file as a template and process it on the server. The HTML form is already created for form processing in the Mobile App; we just need to make it available to the DMS processor on the server. This can be done automatically via CI pipelines.

In server-side DMS processing, the Mobile App simply sends the form data plus the metadata in JSON format to the server.

![DMS Processing on Server](server-dms-processing.png)

Benefits of processing DMS documents on the server:
- avoid document loss: a current limitation of DMS synchronization requires the user to be logged in the Mobile App, which in some cases results in document loss,
- consistency: ensures that all documents are generated using the same templates, reducing inconsistencies caused by outdated or modified templates on mobile devices,
- smaller Mobile App: removing templates from the app reduces the size of the app,
- optimized synchronization: JSON is smaller than HTML, reducing data transfer during synchronization,
- simplified maintenance: less client-side logic means fewer errors and easier updates to the mobile app,
- less processing load: moves HTML generation from mobile (which may have limited resources) to the server,
- easier template updates: templates can be updated on the server without needing users to update the mobile app,
- server-side resources: leverage server power for intensive template processing,
- easier server scaling: handle increased server load without impacting mobile performance,
- direct server-to-server synchronization: reduce mobile dependency for DMS synchronization,
- error handling: the server can retry failed synchronizations more reliably than mobile devices,
- flexibility: easier support for new document formats or integrations (e.g. PDF, DOCX).

## External Services
To refactor the battery measurement and location detection, we need to have the [FSMS Service](#tbd-windows-fsms-service) created. First, we need to update the FSMS Service: add the battery measurement logic, run it periodically, and save the measurements to local storage; add the endpoint to the REST controller.

For location detection service, things are similar.

You can see that the battery and location services in the Mobile App are much simplified; they just invoke a REST API to a known URL instead of creating and managing an external process. They also no longer block, as the values ​​are delivered from the FSMS Service's local storage.

![External Process Fix](external-process-fix.png)

Both battery and location values ​​can be sent to a central server if needed.

Benefits of moving-out external services to FSMS Service:
- simplifies the Mobile App logic: the Mobile App no longer manages complex external processes; it simply invokes a REST API to a known endpoint,
- non-blocking operations: the Mobile App no longer blocks while waiting for measurements, as values are delivered directly from the FSMS Service's local storage,
- centralized data management: battery and location data are stored and managed in a single, consistent way via the FSMS Service,
- improved efficiency: periodic measurements are handled by a single service, reducing redundant computations,
- easy data collection: data can be seamlessly forwarded to a central server if needed.

## Server Push
As mentioned in the design flaw [periodic requests](#periodic-requests), checking for task updates is not optimal.

An elegant solution is to replace the periodic checking with near real-time server notifications, i.e. server push, supported by the proposed [REST server](#rest-server).

![Concept Server Push](server-push.png)

The mobile application opens a permanent connection to the REST server. This connection is idle, with no traffic, and used only when the server has notifications to send. The server is aware of each connected tablet and knows in real time whether a tablet is connected and ready for push notifications.

The REST server communicates with the backoffice via the existing API - path (1) in the diagram. When it discovers a change worth informing, the mobile application creates a notification and push it to the appropriate tablet. Alternatively, the REST server can directly access the backoffice database - path (2) in the diagram.

Note that the push connection between the mobile application and the REST server may be over mobile data. For this reason, the server takes care to send only the differences, if any, and to reduce the size of the notifications by archiving them.

Benefits of implementing server push:
- reduces delays in task data synchronization, ensuring that users receive updates almost instantly,
- minimizes unnecessary query requests, reducing network bandwidth usage,
- reduces CPU and battery usage by eliminating frequent background checks for updates,
- reduces the load on back-office servers by handling updates more efficiently compared to the query-based approach; note: true only if using path (2) from diagram.

Once the server push mechanism implemented, we can also imagine new applications, such as real-time alerts to all tablets or only a group, and chat.

## Logging Server
This update requires [FSMS Service](#fsms-windows-service). The basic functionality is simple - it collects log files from tablets and sends them to a centralized logging server.

The mobile application generates log files on the tablet's file system. The FSMS Service includes a logging agent that:
- retrieves log records from files,
- formats them into a JSON-based structured GELF format,
- sends them to the logging server.

The logging server collects GELF records, stores them in a document database, and updates the text index. If the processed log record indicates a fatal error, an alert is created. There are several open-source options for the logging server; it does not matter which one is used, as long as it covers the described functionality.

![Logging Server Concept](logging-server.png)

Benefits of using centralized logging:
- using structured logs in the GELF format allows for fine-grained filtering,
- searching for indexed text on the logging server is better than Ctrl-F in log files,
- real-time alerts immediately notify the support team via email or SMS when fatal errors occur,
- aggregated logs provide a single source of truth and allow for correlation of errors occurring across multiple tablets,
- historical log retention makes it easier to detect faulty usage patterns,
- manage high-volume logs without overloading tablets.

### Code Instrumentation
Code instrumentation is about collecting usage metrics. They are essential in evaluating changes and in confirming that we are on the right track. They are the only relatively objective references we can have to ensure that the refactoring is truly improving the quality of the code.

Before making any architectural changes, we monitor the collected metrics and create some statistics. After the change, we collect the metrics again and compare them to assess the impact of the change.

![Code Instrumentation](code-instrumentation.png)

Code instrumentation uses the same [logging server](#logging-server) used for centralizing Mobile App logs. The only difference is that we need to update the codebase and insert metrics at the relevant insertion points.

Benefits of code instrumentation:
- objective decision-making: code instrumentation provides measurable data, eliminating guesswork and enabling evidence-based improvements,
- refactoring validation: track metrics before and after changes to confirm that refactoring truly enhances code quality,
- performance benchmarking: establish baselines to compare the impact of optimizations and architectural shifts,
- early anomaly detection: identify unexpected behaviors, inefficiencies, or bottlenecks in real-world usage,
- centralized monitoring: reuse the existing logging server to unify metrics and logs without additional overhead,
- iterative optimization: use historical trends to guide continuous, incremental improvements over time,
- proactive maintenance: proactively address issues revealed by metrics before they escalate into larger problems.

## Static Dictionaries on Server
Here is the solution for the [static dictionaries](#static-dictionaries) implementation flaw.

Static dictionaries transfer is not a complicated process, as it is identical to the server-side dictionary updates, which are performed by our support team anyway. But it can take several days as effort due to the number of records that need to be updated. When done, Mobile App developers should remove static dictionaries logic.

Benefits of moving static dictionaries to the server:
- dictionary maintenance is controlled exclusively by the support team,
- simplification of the mobile application code base by eliminating the management of static dictionaries,
- debugging becomes easier, since we know for sure where the dictionaries are located.

Related to this topic: we can create a simple web application for managing and documenting dictionaries.

# Development & Testing
Refactoring mobile apps is extremely complex, especially it must be done on a continuous delivery product. Because we have to adapt the refactoring process, considering that the evolution of the main development line is impossible to plan ahead.

The only thing for sure is that we need to first clean up the code base, then prepare tools to measure the performance of the application and make sure that we are alerted in case of fatal errors.

We need to be able to assess the state of the system at any time. For this, real-time reporting tools may be needed. These may be provided by the logging server, or we may need to build some reports. It remains to be seen.

Refactoring means much more opportunities for errors than regular code maintenance. We need to keep a close eye on regressions! Only then can we start refactoring.

We also need to automate the build process and use pilot-based deployment. It is reasonable and prudent to be prepared for rollbacks.

Testing is not a problem in itself, as we need to develop including refactoring, using the TDD - Test Driven Development methodology, so that tests become an integrated and active part of the development process. Note that in this context, tests only refer to automated unit tests. Integration and user acceptance testing are performed as usual.

We could probably start refactoring with Java and JavaFX upgrade to version 21. This requires resolving dependencies on Jakarta EE, as Java EE is no longer part of the Java distribution. This Java EE update requires source code updates, as the _javax_ package is renamed to _jakarta_. It also requires downloading the JavaFX SDK as a separate artifact, as starting with Java 9 FX is no longer part of the Java distribution. This Java 21 update should be properly tested, deployed to production using a pilot, and monitored. It has a relatively high risk of regressions.

# Glossary

| Term       | Definition |
|------------|------------|
| API        | Application Programming Interface |
| BU         | Business Unit | 
| CDI        | Context and Dependency Injection |
| Code Instrumentation | The process of inserting additional code into a program to gather runtime information such as performance metrics |
| CRUD       | Create Read Update Delete: basic operation specific to databases; CRUD is used as a synonymous for database |
| DMS        | Document Management System |
| DSL        | Domain Specific Language |
| ERP        | Enterprise Resource Planning |
| FFA        | Field Force Automation |
| FSMS       | Field Service Management System |
| GELF       | Graylog Extended Log Format: structured log record format based on JSON |
| GUI        | Graphical User Interface |
| HLD        | High Level Design |
| IOC        | Inversion Of Control: Spring name for CDI |
| Java EE    | Java Enterprise Edition |
| JAX-RS     | Jakarta RESTful Web Services |
| JAX-RS SSE | Server-Sent Events: Java API for server push |
| JVM        | Java Virtual Machine |
| KLOC       | Kilo Lines Of Code |
| OMS        | Outage Management System |
| SAP        | Systems, Applications, and Products in Data Processing |
| SAP DM     | SAP Device Management |
| SAP IS-U   | Industry-Specific Solution for the Utilities Industry |
| Server Push | Communication style used in client-server architectures where server send events in real time to client |
| SOAP       | Simple Object Access Protocol |
| UAT        | User Acceptance Testing: tests performed by business unit to ensure delivered changes are conform |

