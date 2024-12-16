#########################################################
5. Пример итогово XML файла для создания виртуальной сети
#########################################################



| <network connections=\"1\">
|   <name>ovs-virtnet</name>
|   <uuid>203616c8-c2ff-4f6b-ba14-dfb13951d492</uuid>
|   <forward mode=\"bridge"/>
|   <bridge name="test-br"/>
|   <virtualport type=\"openvswitch\"/>
|   <portgroup name=\"vlan-10\">
|     <vlan>
|       <tag id=\"10\"/>
|     </vlan>
|   </portgroup>
|   <portgroup name=\"vlan-20\">
|     <vlan>
|       <tag id=\"20\"/>
|     </vlan>
|   </portgroup>
|   <portgroup name=\"vlan-30\">
|     <vlan>
|       <tag id=\"30\"/>
|     </vlan>
|   </portgroup>
|   <portgroup name=\"vlan-40\">
|     <vlan>
|       <tag id=\"40\"/>
|     </vlan>
|   </portgroup>
|   <portgroup name=\"vlan-50\">
|     <vlan>
|       <tag id=\"50\"/>
|     </vlan>
|   </portgroup>
|   <portgroup name=\"vlan-90\">
|     <vlan>
|       <tag id=\"90\"/>
|     </vlan>
|   </portgroup>
|   <portgroup name=\"trunk\">
|     <vlan trunk=\"yes\">
|       <tag id=\"30\"/>
|       <tag id=\"40\"/>
|       <tag id=\"50\"/>
|     </vlan>
|   </portgroup>
| </network>