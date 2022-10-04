/*
order_sentence_filters.prg
~~~~~~~~~~~~~~~~~~~~
Gets order sentence filters based on the PowerPlan
Save to: data/os_filter_b0783.csv or data/os_filter_p0783.csv
*/
select osf.*
from order_sentence os
    , pathway_comp pc
    , pw_comp_os_reltn pcos
    , order_sentence_filter osf
    , pathway_catalog pwcat
    , pathway_catalog pwcat2
    , pw_cat_reltn pcr
plan pwcat where pwcat.active_ind = 1
    and pwcat.type_mean in ("CAREPLAN", "PATHWAY")
    and pwcat.description_key like "ONCP*"
    and pwcat.version = (
        select max(pwcat4.version)
        from pathway_catalog pwcat4
        where pwcat4.version_pw_cat_id = pwcat.version_pw_cat_id
            and pwcat4.active_ind = 1
    )
    and pwcat.end_effective_dt_tm > cnvtdatetime(curdate,curtime3)
    and pwcat.pathway_type_cd in (
        value(uar_get_code_by("DISPLAY_KEY", 30183, "ONCOLOGY"))
        , value(uar_get_code_by("DISPLAY_KEY", 30183, "COMPASSIONATEACCESSPROGRAM"))
        , value(uar_get_code_by("DISPLAY_KEY", 30183, "ONCOLOGYMULTIDISCIPLINARY"))
    )
join pcr where pcr.pw_cat_s_id = outerjoin(pwcat.pathway_catalog_id)
    and pcr.type_mean = outerjoin("GROUP")
join pwcat2 where pwcat2.pathway_catalog_id = outerjoin(pcr.pw_cat_t_id)
join pc where pc.active_ind = 1
    and pc.pathway_catalog_id in (
        pwcat.pathway_catalog_id
        , pwcat2.pathway_catalog_id
    )
join pcos where pcos.pathway_comp_id = pc.pathway_comp_id
join os where os.order_sentence_id = pcos.order_sentence_id
join osf where osf.order_sentence_id = os.order_sentence_id
    and osf.order_sentence_id > 0
with uar_code(d)