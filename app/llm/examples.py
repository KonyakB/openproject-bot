FEW_SHOT_EXAMPLES = """Example 1
Input: create a new issue in space1 for electronics, design pcb
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"Design PCB","description":"Create PCB design task for electronics.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.95,"ambiguities":[]}

Example 2
Input: make a bug in space1: power rail drops under load
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Bug","subject":"Power Rail Drops Under Load","description":"Investigate voltage drop under load conditions.","custom_fields":{"Domain":"electronics"},"priority_ref":"High","assignee_ref":null,"due_date":null,"confidence":0.93,"ambiguities":[]}

Example 3
Input: in demo project create feature for export csv in reports
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Feature","subject":"Add CSV Export To Reports","description":"Implement CSV export in reporting module.","custom_fields":{"Domain":"software"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.94,"ambiguities":[]}

Example 4
Input: space1 task: update schematic symbols
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"Update Schematic Symbols","description":"Revise and standardize schematic symbols.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.92,"ambiguities":[]}

Example 5
Input: create issue in alpha for firmware boot timeout
Output: {"action":"create_work_package","project_ref":"alpha","type_ref":"Bug","subject":"Firmware Boot Timeout","description":"Boot occasionally times out during startup.","custom_fields":{"Domain":"firmware"},"priority_ref":"High","assignee_ref":null,"due_date":null,"confidence":0.91,"ambiguities":[]}

Example 6
Input: new task in mech project: redesign mounting bracket
Output: {"action":"create_work_package","project_ref":"mech","type_ref":"Task","subject":"Redesign Mounting Bracket","description":"Redesign bracket for strength and manufacturability.","custom_fields":{"Domain":"mechanical"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.94,"ambiguities":[]}

Example 7
Input: create story in app project for onboarding checklist
Output: {"action":"create_work_package","project_ref":"app","type_ref":"Story","subject":"Onboarding Checklist Flow","description":"Implement onboarding checklist flow for new users.","custom_fields":{"Domain":"software"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.9,"ambiguities":[]}

Example 8
Input: in space1 create task for emi testing prep due 2026-05-01
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"Prepare For EMI Testing","description":"Prepare materials and setup for EMI testing.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":"2026-05-01","confidence":0.94,"ambiguities":[]}

Example 9
Input: demo create bug login fails on safari
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Bug","subject":"Login Fails On Safari","description":"Users cannot log in using Safari browser.","custom_fields":{"Domain":"software"},"priority_ref":"High","assignee_ref":null,"due_date":null,"confidence":0.93,"ambiguities":[]}

Example 10
Input: space1 create task documentation for pcb bringup
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"Document PCB Bring-Up","description":"Write bring-up procedure and checklist.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.92,"ambiguities":[]}

Example 11
Input: space1 bug pcb trace too thin rev b
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Bug","subject":"PCB Trace Too Thin On Rev B","description":"Trace width issue observed on Rev B board.","custom_fields":{"Domain":"electronics"},"priority_ref":"High","assignee_ref":null,"due_date":null,"confidence":0.9,"ambiguities":[]}

Example 12
Input: demo task clean up api error handling
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Task","subject":"Clean Up API Error Handling","description":"Standardize API error handling paths.","custom_fields":{"Domain":"software"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.89,"ambiguities":[]}

Example 13
Input: alpha feature ota rollback support
Output: {"action":"create_work_package","project_ref":"alpha","type_ref":"Feature","subject":"Add OTA Rollback Support","description":"Add rollback support to OTA updates.","custom_fields":{"Domain":"firmware"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.9,"ambiguities":[]}

Example 14
Input: mech task tighten tolerance on housing
Output: {"action":"create_work_package","project_ref":"mech","type_ref":"Task","subject":"Tighten Housing Tolerances","description":"Refine housing tolerances for fit consistency.","custom_fields":{"Domain":"mechanical"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.88,"ambiguities":[]}

Example 15
Input: space1 task add test points adc lines
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"Add Test Points To ADC Lines","description":"Add ADC test points to improve diagnostics.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.9,"ambiguities":[]}

Example 16
Input: demo bug flaky ci on integration tests
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Bug","subject":"Flaky CI Integration Tests","description":"Investigate intermittent integration test failures in CI.","custom_fields":{"Domain":"software"},"priority_ref":"Medium","assignee_ref":null,"due_date":null,"confidence":0.89,"ambiguities":[]}

Example 17
Input: space1 create task power sequencing checklist
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"Power Sequencing Checklist","description":"Create checklist for board power sequencing.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.88,"ambiguities":[]}

Example 18
Input: app bug notifications duplicate on refresh
Output: {"action":"create_work_package","project_ref":"app","type_ref":"Bug","subject":"Duplicate Notifications On Refresh","description":"Notifications duplicate when page refreshes.","custom_fields":{"Domain":"software"},"priority_ref":"Medium","assignee_ref":null,"due_date":null,"confidence":0.9,"ambiguities":[]}

Example 19
Input: alpha task uart logs for boot stages
Output: {"action":"create_work_package","project_ref":"alpha","type_ref":"Task","subject":"Add UART Logs For Boot Stages","description":"Emit UART logs at each boot stage.","custom_fields":{"Domain":"firmware"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.89,"ambiguities":[]}

Example 20
Input: demo feature bulk import users csv
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Feature","subject":"Bulk Import Users From CSV","description":"Implement bulk user import from CSV files.","custom_fields":{"Domain":"software"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.9,"ambiguities":[]}

Example 21
Input: create issue for electronics, design pcb
Output: {"action":"create_work_package","project_ref":null,"type_ref":"Task","subject":"Design PCB","description":"Create PCB design task for electronics.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.73,"ambiguities":["Project not specified"]}

Example 22
Input: space1 create issue for routing
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"PCB Routing Task","description":"Create routing task in project.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.76,"ambiguities":["Subject inferred from vague request"]}

Example 23
Input: create bug in demo
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Bug","subject":null,"description":"Bug creation requested in demo project.","custom_fields":{},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.68,"ambiguities":["Subject missing"]}

Example 24
Input: task in alpha for bootloader
Output: {"action":"create_work_package","project_ref":"alpha","type_ref":"Task","subject":"Bootloader Improvements","description":"Task related to bootloader work.","custom_fields":{"Domain":"firmware"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.75,"ambiguities":["Subject partially inferred"]}

Example 25
Input: new issue project space1 assign to alice
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":null,"description":"Create issue and assign to alice.","custom_fields":{},"priority_ref":null,"assignee_ref":"alice","due_date":null,"confidence":0.7,"ambiguities":["Subject missing"]}

Example 26
Input: in app create feature
Output: {"action":"create_work_package","project_ref":"app","type_ref":"Feature","subject":null,"description":"Feature requested in app project.","custom_fields":{},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.66,"ambiguities":["Subject missing"]}

Example 27
Input: create issue in space1 for electrical
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":null,"description":"Issue requested for electrical domain.","custom_fields":{"Domain":"electrical"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.69,"ambiguities":["Subject missing","Custom field value may not match allowed candidates"]}

Example 28
Input: demo story user can reset password
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Story","subject":"User Can Reset Password","description":"Implement password reset user story.","custom_fields":{"Domain":"software"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.85,"ambiguities":[]}

Example 29
Input: mech create task
Output: {"action":"create_work_package","project_ref":"mech","type_ref":"Task","subject":null,"description":"Task requested in mech project.","custom_fields":{"Domain":"mechanical"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.64,"ambiguities":["Subject missing"]}

Example 30
Input: space1 create new work package due next friday for emi
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"EMI Preparation","description":"Create EMI-related work package.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.72,"ambiguities":["Relative due date not normalized"]}

Example 31
Input: create issue in space project for electronics
Output: {"action":"create_work_package","project_ref":"space","type_ref":"Task","subject":null,"description":"Issue requested for electronics.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.62,"ambiguities":["Project may refer to multiple matches","Subject missing"]}

Example 32
Input: make one in demo2 maybe demo idk, fix login
Output: {"action":"create_work_package","project_ref":"demo2","type_ref":"Bug","subject":"Fix Login","description":"Login fix requested.","custom_fields":{"Domain":"software"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.55,"ambiguities":["Project reference uncertain between demo2 and demo"]}

Example 33
Input: add task for wiring harness in project a
Output: {"action":"create_work_package","project_ref":"a","type_ref":"Task","subject":"Wiring Harness Task","description":"Work on wiring harness.","custom_fields":{"Domain":"mechanical"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.58,"ambiguities":["Project reference too short and potentially ambiguous"]}

Example 34
Input: space1 bug maybe medium priority maybe high, adc unstable
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Bug","subject":"ADC Unstable Readings","description":"ADC behavior appears unstable.","custom_fields":{"Domain":"electronics"},"priority_ref":"High","assignee_ref":null,"due_date":null,"confidence":0.61,"ambiguities":["Priority conflict in request: medium vs high"]}

Example 35
Input: create issue in app and assign john
Output: {"action":"create_work_package","project_ref":"app","type_ref":"Task","subject":null,"description":"Issue requested and assignment requested for john.","custom_fields":{"Domain":"software"},"priority_ref":null,"assignee_ref":"john","due_date":null,"confidence":0.67,"ambiguities":["Subject missing","Assignee may be unresolved"]}

Example 36
Input: need a thing in demo project
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Task","subject":null,"description":"User requested a new work item.","custom_fields":{},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.41,"ambiguities":["Subject missing","Type inferred from vague language"]}

Example 37
Input: space1 feature or task for board bringup notes
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"Board Bring-Up Notes","description":"Create and maintain board bring-up notes.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.57,"ambiguities":["Type ambiguous: feature or task"]}

Example 38
Input: create in alpha for fw, due soon
Output: {"action":"create_work_package","project_ref":"alpha","type_ref":"Task","subject":"Firmware Task","description":"Create firmware-related task.","custom_fields":{"Domain":"firmware"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.6,"ambiguities":["Subject too generic","Relative due date not normalized"]}

Example 39
Input: project demo create issue domain = hw-sw co-design
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Task","subject":null,"description":"Create issue for HW-SW co-design.","custom_fields":{"Domain":"hw-sw co-design"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.59,"ambiguities":["Subject missing","Custom field value may be invalid"]}

Example 40
Input: space1 create bug assign to bence arek due 2026/05/10
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Bug","subject":null,"description":"Bug requested and assignment requested for bence arek.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":"bence arek","due_date":"2026-05-10","confidence":0.63,"ambiguities":["Subject missing","Assignee may be unresolved"]}

Example 41
Input: pls make ticket in space1: pcb gerber mismatch vs bom
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Bug","subject":"Gerber Mismatch Versus BOM","description":"Mismatch between PCB Gerber files and BOM.","custom_fields":{"Domain":"electronics"},"priority_ref":"High","assignee_ref":null,"due_date":null,"confidence":0.88,"ambiguities":[]}

Example 42
Input: cre8 task demo refactor auth middleware
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Task","subject":"Refactor Auth Middleware","description":"Refactor authentication middleware for maintainability.","custom_fields":{"Domain":"software"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.84,"ambiguities":[]}

Example 43
Input: space1 yeni issue olustur: sensor kalibrasyon akisi
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"Sensor Kalibrasyon Akisi","description":"Create task for sensor calibration flow.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.77,"ambiguities":[]}

Example 44
Input: demo project bug login failure
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Bug","subject":"Login Failure","description":"Create bug for login failure.","custom_fields":{"Domain":"software"},"priority_ref":"High","assignee_ref":null,"due_date":null,"confidence":0.74,"ambiguities":["Language normalization applied"]}

Example 45
Input: space1: task -> emc precheck, owner alice, prio high
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"Run EMC Precheck","description":"Perform EMC precheck before formal test.","custom_fields":{"Domain":"electronics"},"priority_ref":"High","assignee_ref":"alice","due_date":null,"confidence":0.86,"ambiguities":["Assignee may need exact user mapping"]}

Example 46
Input: alpha create issue: boot loop after OTA v1.2.3
Output: {"action":"create_work_package","project_ref":"alpha","type_ref":"Bug","subject":"Boot Loop After OTA v1.2.3","description":"Device enters boot loop after OTA update v1.2.3.","custom_fields":{"Domain":"firmware"},"priority_ref":"High","assignee_ref":null,"due_date":null,"confidence":0.9,"ambiguities":[]}

Example 47
Input: add work package in app for dark mode maybe later
Output: {"action":"create_work_package","project_ref":"app","type_ref":"Feature","subject":"Add Dark Mode","description":"Implement dark mode support.","custom_fields":{"Domain":"software"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.78,"ambiguities":["Timeline unclear: 'maybe later'"]}

Example 48
Input: create ticket for rev c board bringup in space1 and maybe demo
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"Rev C Board Bring-Up","description":"Prepare and execute Rev C board bring-up.","custom_fields":{"Domain":"electronics"},"priority_ref":null,"assignee_ref":null,"due_date":null,"confidence":0.58,"ambiguities":["Project ambiguous between space1 and demo"]}

Example 49
Input: in demo create urgent bug: payment webhook retries explode
Output: {"action":"create_work_package","project_ref":"demo","type_ref":"Bug","subject":"Payment Webhook Retry Storm","description":"Webhook retries spike unexpectedly and cause failures.","custom_fields":{"Domain":"software"},"priority_ref":"Urgent","assignee_ref":null,"due_date":null,"confidence":0.87,"ambiguities":[]}

Example 50
Input: space1 task: design umls, add bence arek as assignee
Output: {"action":"create_work_package","project_ref":"space1","type_ref":"Task","subject":"Design UMLs","description":"Create UML design task.","custom_fields":{"Domain":"software"},"priority_ref":null,"assignee_ref":"bence arek","due_date":null,"confidence":0.82,"ambiguities":["Assignee may be unresolved in OpenProject"]}
"""
