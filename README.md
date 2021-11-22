# OpenStack CCloud CLI Extension for adding/removing members to/from server-groups

This plugin adds the commands ``openstack server group add members`` and
``openstack server group remove members`` for adding/removing members of a
server-group. The actions are done through an extension of Nova's API available
in CC+1. That extension might not become available upstream.
