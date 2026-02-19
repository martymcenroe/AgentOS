# Extracted Test Plan

## Scenarios

### test_id
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Test Description | Expected Behavior | Status

### test_t010
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Tab navigation test | All tabs navigate without blank screens | RED

### test_t020
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Tab persistence test | Hash and query params persist on refresh | RED

### test_t030
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Conversation detail test | Rate, label, back button work correctly | RED

### test_t040
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Admin bulk actions test | Filter, select, poke, re-init work | RED

### test_t050
- Type: unit
- Requirement: 
- Mock needed: False
- Description: STARRED filter test | STARRED chip returns STARRED results | RED

### test_t060
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Auto-polling test | Polling starts/stops on tab change | RED

### test_t070
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Edge cases test | Empty state, deep links, rapid switching | RED

### test_010
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Nav to each tab | Auto | Click each tab | Content loads, no blank | Tab container visible

### test_020
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Conversation nav returns to list | Auto | Click conv, then nav | List visible, not blank | #conv-list displayed

### test_030
- Type: unit
- Requirement: 
- Mock needed: False
- Description: URL hash updates | Auto | Switch tabs | Hash matches tab name | location.hash correct

### test_040
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Refresh preserves tab | Auto | Refresh on #admin | Admin tab active | #admin in URL, admin visible

### test_050
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Refresh preserves query | Auto | Refresh with ?key= | Key preserved | Query param intact

### test_060
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Conv detail shows data | Auto | Click conversation | Messages, labels, rating | Detail panel populated

### test_070
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Rate conversation | Auto | Click rating | Toast appears, rating saved | API called, toast visible

### test_080
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Back refreshes list | Auto | Rate then back | Updated rating in list | Rating visible in row

### test_090
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Add label | Auto | Add label to conv | Label appears | Label in DOM

### test_100
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Remove label | Auto | Remove label | Label disappears | Label not in DOM

### test_110
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Filter by state | Auto | Select state filter | List updates | Only matching convs

### test_120
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Filter by label | Auto | Select label filter | List updates | Only matching convs

### test_130
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Admin auto-load | Auto | Open admin tab | Convs load without click | Preview populated

### test_140
- Type: unit
- Requirement: 
- Mock needed: False
- Description: State chip toggle | Auto | Click chip | Selected style | CSS class applied

### test_150
- Type: unit
- Requirement: 
- Mock needed: False
- Description: STARRED filter works | Auto | STARRED chip + Load | STARRED convs shown | STARRED in results

### test_160
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Multi-chip filter | Auto | Select multiple | AND filter applied | Intersection shown

### test_170
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Label dropdown populated | Auto | Open admin | Labels with counts | Dropdown has options

### test_180
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Time filter recent | Auto | 30 min filter | Recent convs only | Filtered by time

### test_190
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Time filter blank | Auto | Clear time filter | All convs shown | No time filtering

### test_200
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Checkbox selection | Auto | Check boxes | Bulk bar appears | Bulk bar with count

### test_210
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Select all | Auto | Click select all | All rows selected | All checkboxes checked

### test_220
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Poke selected | Auto | Poke action | Working state, then refresh | States updated

### test_230
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Auto | States reset to INITIAL | States are INITIAL

### test_240
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Polling starts after poke | Auto | Poke then wait | Requests every 3s | Network activity

### test_250
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Polling stops on tab change | Auto | Poke, switch tab | No more requests | No network activity

### test_260
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Polling stops on nav away | Auto | Navigate away | No background requests | No network activity

### test_270
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Empty state message | Auto | Filter no matches | Message shown | "No matching" text

### test_280
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Deep link conv | Auto | ?conv=123 | Detail opens | Detail visible

### test_290
- Type: unit
- Requirement: 
- Mock needed: False
- Description: Deep link invalid | Auto | ?conv=999 | Graceful handling | No crash, error shown

### test_300
- Type: unit
- Requirement: 
- Mock needed: True
- Description: Rapid tab switching | Auto | Click tabs fast | No stale content | Correct content

