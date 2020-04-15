select os.order_sentence_id
    , osd.oe_field_display_value
    , order_entry_field = oef.description
from order_sentence os
    , order_sentence_detail osd
    , order_entry_fields oef
    , pathway_comp pc
    , pathway_catalog pwcat
    , pw_comp_os_reltn pcos
plan pwcat where pwcat.active_ind = 1
    and pwcat.end_effective_dt_tm > sysdate
    and pwcat.beg_effective_dt_tm < sysdate
    and pwcat.type_mean != 'PHASE'
;    and pwcat.type_mean = 'PHASE'
join pc where pc.pathway_catalog_id = pwcat.pathway_catalog_id
    and pc.active_ind = 1
    and pc.parent_entity_name = 'ORDER_CATALOG_SYNONYM'
join pcos where pcos.pathway_comp_id = pc.pathway_comp_id
join os where os.order_sentence_id = pcos.order_sentence_id
join osd where osd.order_sentence_id = os.order_sentence_id
join oef where oef.oe_field_id = osd.oe_field_id