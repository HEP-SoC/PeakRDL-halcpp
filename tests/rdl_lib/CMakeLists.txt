add_ip(addrmap_rw)
ip_sources(${IP} SYSTEMRDL addrmap_rw.rdl)

add_ip(addrmap_ro)
ip_sources(${IP} SYSTEMRDL addrmap_ro.rdl)

add_ip(addrmap_wo)
ip_sources(${IP} SYSTEMRDL addrmap_wo.rdl)

add_ip(addrmap_mixed_access)
ip_sources(${IP} SYSTEMRDL addrmap_mixed_access.rdl)


add_ip(addrmap_rw_reg_1d_array)
ip_sources(${IP} SYSTEMRDL ./addrmap_rw_reg_1d_array.rdl)

add_ip(addrmap_rw_reg_2d_array)
ip_sources(${IP} SYSTEMRDL ./addrmap_rw_reg_2d_array.rdl)

add_ip(addrmap_rw_reg_4d_array)
ip_sources(${IP} SYSTEMRDL ./addrmap_rw_reg_4d_array.rdl)

add_ip(addrmap_hier_rw)
ip_sources(${IP} SYSTEMRDL ./addrmap_hier_rw.rdl)
ip_link(${IP} addrmap_rw)

add_ip(addrmap_hier_ro)
ip_sources(${IP} SYSTEMRDL ./addrmap_hier_ro.rdl)
ip_link(${IP} addrmap_ro)

add_ip(addrmap_hier_wo)
ip_sources(${IP} SYSTEMRDL ./addrmap_hier_wo.rdl)
ip_link(${IP} addrmap_wo)

add_ip(addrmap_hier_mixed)
ip_sources(${IP} SYSTEMRDL ./addrmap_hier_mixed.rdl)
ip_link(${IP} addrmap_ro addrmap_wo addrmap_rw)

add_ip(addrmap_hier_mixed2)
ip_sources(${IP} SYSTEMRDL ./addrmap_hier_mixed2.rdl)
ip_link(${IP} addrmap_ro addrmap_wo addrmap_rw addrmap_mixed_access)

add_ip(addrmap_hier_rw_reg_arrays)
ip_sources(${IP} SYSTEMRDL ./addrmap_hier_rw_reg_arrays.rdl)
ip_link(${IP} addrmap_rw_reg_1d_array addrmap_rw_reg_2d_array addrmap_rw_reg_4d_array)
