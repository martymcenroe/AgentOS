# Extracted Test Plan

## Scenarios

### test_010
- Type: integration
- Requirement: 
- Mock needed: False
- Description: Happy path - LLD archived | integration | State with valid LLD path in active/ | LLD moved to done/, path returned | File exists in done/, not in active/, log contains success message

### test_020
- Type: integration
- Requirement: 
- Mock needed: False
- Description: Happy path - Reports archived | integration | State with report paths in active/ | Reports moved to done/ | Files exist in done/, not in active/, log contains success message

### test_030
- Type: integration
- Requirement: 
- Mock needed: False
- Description: LLD not found | integration | State with non-existent LLD path | Warning logged, None returned | No exception, log contains warning

### test_040
- Type: integration
- Requirement: 
- Mock needed: False
- Description: LLD not in active/ | integration | State with LLD in arbitrary path | Skip archival, None returned | File unchanged, log indicates skip

### test_050
- Type: integration
- Requirement: 
- Mock needed: False
- Description: done/ doesn't exist | integration | Valid LLD, no done/ directory | done/ created, LLD moved | Directory created, file moved

### test_060
- Type: integration
- Requirement: 
- Mock needed: False
- Description: Destination file exists | integration | LLD exists in both active/ and done/ | Append timestamp to new name | No overwrite, both files preserved

### test_070
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Empty state | unit | State with no paths | Graceful no-op | No exception, empty archival list

### test_080
- Type: integration
- Requirement: 
- Mock needed: False
- Description: Mixed success | integration | Some files exist, some don't | Archive existing, log missing | Partial archival succeeds

### test_090
- Type: integration
- Requirement: 
- Mock needed: False
- Description: Workflow failed - no archival | integration | State with workflow_success=False, valid LLD path | No files moved, skip logged | Files remain in active/, log indicates skip

