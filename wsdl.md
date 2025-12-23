# WSDL Processing

List of XML web service endpoints processed by Maven on API module.

In below list all packages belong to `com.globema.ant.webservices` package and all endpoints are prefixed with `/G4/servlet/WSDL/`. For example full `get_messages` package is `com.globema.ant.webservices.get_messages` and its related endpoint is `/G4/servlet/WSDL/GetMessages_Mobile_1.01`. Full endpoint URL is `http://ffa.globema.pl/G4/servlet/WSDL/GetMessages_Mobile_1.01` where hostname ffa.globema.pl is resolved on test app server #1, 10.138.95.137 .

| Endpoint | Package |
|----------|---------|
| [AlertDispatcher_Mobile_1.00](AlertDispatcher_Mobile_1.00.md) | alert_dispatcher |
| [AlertDispatcherFormation_Mobile_1.00](AlertDispatcherFormation_Mobile_1.00.md) | alert_dispatcher_formation |
| [AssignCar_Mobile_1.00](AssignCar_Mobile_1.00.md) | log_mobile_message |
| [CloneFraudGas_Mobile_1_00](CloneFraudGas_Mobile_1_00.md) | clone_fraud_gas |
| [DeleteMessages_Mobile_1.00](DeleteMessages_Mobile_1.00.md) | delete_messages |
| GetActions_Mobile_1.00 | get_actions |
| GetActions_Mobile_1.01 | get_actions |
| GetActions_Mobile_1.02 | get_actions |
| GetActions_Mobile_1.03 | get_actions |
| GetActions_Mobile_1.04 | get_actions |
| [GetActions_Mobile_1.05](GetActions_Mobile_1.05.md) | get_actions |
| GetAddresses_Mobile_1.00 | get_addresses |
| [GetAddresses_Mobile_1.01](GetAddresses_Mobile_1.01.md) | get_addresses |
| [GetCars_Mobile_1.00](GetCars_Mobile_1.00.md) | log_mobile_message |
| GetDictionaries_Mobile_1.00 | get_dictionary |
| GetDictionaries_Mobile_1.01 | get_dictionary |
| [GetDictionaries_Mobile_1.02](GetDictionaries_Mobile_1.02.md) | get_dictionary |
| [GetErpOs_Mobile_1.00](GetErpOs_Mobile_1.00.md) | get_erp |
| GetMaterials_Mobile_1.00 | get_materials |
| [GetMaterials_Mobile_1.01](GetMaterials_Mobile_1.01.md) | get_materials |
| GetMessages_Mobile_1.00 | get_messages |
| [GetMessages_Mobile_1.01](GetMessages_Mobile_1.01.md) | get_messages |
| [GetOmsAffectedCustomers_Mobile_1.00](GetOmsAffectedCustomers_Mobile_1.00.md) | get_oms_affected_customers |
| [GetOmsPlannedTask_Mobile_1.00](GetOmsPlannedTask_Mobile_1.00.md) | get_oms_planned_task |
| GetOmsTicket_Mobile_1.00 | get_omsTicket |
| [GetOmsTicket_Mobile_1.01](GetOmsTicket_Mobile_1.01.md) | get_omsTicket |
| GetOS_Mobile_1.00 | get_os |
| GetOS_Mobile_1.01 | get_os |
| [GetOS_Mobile_1.02](GetOS_Mobile_1.02.md) | get_os |
| [GetReadingUnits_Mobile_1.00](GetReadingUnits_Mobile_1.00.md) | get_dm |
| GetSerials_Mobile_1.00 | get_serials |
| GetSerials_Mobile_1.01 | get_serials |
| [GetSerials_Mobile_1.02](GetSerials_Mobile_1.02.md) | get_serials |
| [GetTeam_Mobile_1.00](GetTeam_Mobile_1.00.md) | get_team |
| GetTeamEx_Mobile_1.00 | get_team_ex |
| GetTeamEx_Mobile_1.01 | get_team_ex |
| [GetTeamEx_Mobile_1.02](GetTeamEx_Mobile_1.02.md) | get_team_ex |
| [LogMobileMessage_Mobile_1.00](LogMobileMessage_Mobile_1.00.md) | log_mobile_message |
| [ReportEvent_Mobile_1.00](ReportEvent_Mobile_1.00.md) | report_event |
| [SendAffectedCustomersRequest_Mobile_1.00](SendAffectedCustomersRequest_Mobile_1.00.md) | send_affected_customers_request |
| [SendData_Mobile_1.00](SendData_Mobile_1.00.md) | send_data_chunk_mobile |
| SendErpNotification_Mobile_1.00 | send_erp_notification |
| SendErpNotification_Mobile_1.01 | send_erp_notification |
| [SendErpNotification_Mobile_1.02](SendErpNotification_Mobile_1.02.md) | send_erp_notification |
| SendErpOs_Mobile_1.00 | send_erp_os |
| SendErpOs_Mobile_1.01 | send_erp_os |
| SendErpOs_Mobile_1.02 | send_erp_os |
| SendErpOs_Mobile_1.03 | send_erp_os |
| SendErpOs_Mobile_1.04 | send_erp_os |
| SendErpOs_Mobile_1.05 | send_erp_os |
| SendErpOs_Mobile_1.06 | send_erp_os |
| [SendErpOs_Mobile_1.07](SendErpOs_Mobile_1.07.md) | send_erp_os |
| SendIsuOs_Mobile_1.00 | send_isu_os |
| SendIsuOs_Mobile_1.01 | send_isu_os |
| SendIsuOs_Mobile_1.02 | send_isu_os |
| SendIsuOs_Mobile_1.03 | send_isu_os |
| SendIsuOs_Mobile_1.04 | send_isu_os |
| SendIsuOs_Mobile_1.05 | send_isu_os |
| SendIsuOs_Mobile_1.06 | send_isu_os |
| SendIsuOs_Mobile_1.07 | send_isu_os |
| [SendIsuOs_Mobile_1.08](SendIsuOs_Mobile_1.08.md) | send_isu_os |
| SendIsuOs_Mobile_1.09 | send_isu_os |
| [SendTicketUpdate_Mobile_1.00](SendTicketUpdate_Mobile_1.00.md) | send_ticket_update |
| SentMesseges_Mobile_1.00 | send_messages |
| [SentMesseges_Mobile_1.01](SentMesseges_Mobile_1.01.md) | send_messages |
| UpdateAction_Mobile_1.00 | update_action |
| [UpdateAction_Mobile_1.01](UpdateAction_Mobile_1.01.md) | update_action |
| [UpdateMaterials_Mobile_1.00](UpdateMaterials_Mobile_1.00.md) | update_materials |
| [UsedSerials_Mobile_1.00](UsedSerials_Mobile_1.00.md) | used_serials |

## WSDL Stubs Generation

On `API` module there is project POM file. On plugins section there is AXIS2 WSDL plugin configured to generated classes dealing with SOAP low level communication. There is an `execution` section for every defined endpoint.

```xml
<properties>
	<WSDLurl>http://ffa.globema.pl/</WSDLurl>
</properties>

<plugin>
	<groupId>org.apache.axis2</groupId>
	<artifactId>axis2-wsdl2code-maven-plugin</artifactId>
	<version>1.6.1</version>
	<executions>
		<execution>
			<id>ws1</id>
			<goals>
				<goal>wsdl2code</goal>
			</goals>
			<configuration>
				<packageName>com.globema.ant.webservices.get_actions</packageName>
				<wsdlFile>${WSDLurl}/G4/servlet/WSDL/GetActions_Mobile_1.04</wsdlFile>
				<syncMode>sync</syncMode>
				<unpackClasses>false</unpackClasses>
				<generateServerSide>false</generateServerSide>
				<generateServicesXml>false</generateServicesXml>
			</configuration>
		</execution>
        ...
	</executions>
</plugin>
```

