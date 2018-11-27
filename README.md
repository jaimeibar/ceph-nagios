# ceph-nagios

Tests for monitoring a Ceph cluster from Nagios

Running tests are grouped in four sections.
  * common
    * status
    * health
    * quorum
    * df
  * mon
    * monhealth MONID
    * monstatus
    * monstat
  * osd
    * stat
    * tree
  * mds
    * mdsstat

#### Tests and Ceph commands

| Section | Test | Ceph command | Notes |
| ------- | ---- | ------------ | ----- |
| Common |  |  | |
| | check_ceph_health.py common --status | ceph status | |
| | check_ceph_health.py common --health | ceph health | |
| | check_ceph_health.py common --quorum | ceph quorum_status | |
| | check_ceph_health.py common --df | ceph df | |
| Mon |  |  | |
| | check_ceph_health.py mon --monhealth MONID | ceph ping mon.$MONID |  |
| | check_ceph_health.py mon --monstatus | ceph mon_status | |
| | check_ceph_health.py mon --monstat | ceph mon stat | |
| Osd |  |  | |
| | check_ceph_health.py osd --stat | ceph osd stat | |
| | check_ceph_health.py osd --tree | ceph osd tree | |
| Mds |  |  | |
| | check_ceph_health.py mds --mdsstat | ceph mds stat | |
