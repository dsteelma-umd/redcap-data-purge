from sqlalchemy.ext.automap import generate_relationship
from pprint import pprint

def print_summary(summaryHash):
    for k in summaryHash:
        print(f'{k}: {summaryHash[k]}')

def sqlalchemy_gen_relationship(base, direction, return_fn, attrname, local_cls, referred_cls, **kw):
    return generate_relationship(base, direction, return_fn, attrname+'_ref', local_cls, referred_cls, **kw)

def name_for_scalar_relationship(base, local_cls, referred_cls, constraint):
    name = referred_cls.__name__.lower()
    local_table = local_cls.__table__
    if name in local_table.columns:
        newname = name + "_"
        print(f'Already detected name {name} present.  using {newname}')
        return newname
    return name

def get_table_id_mapping():
    return {}

def get_id_field_for_table(table):
    return get_table_id_mapping().get(table)

def compare_database_automaps(db1, db2):
    matching = True
    matching = compare_table_relations(db1.table_relations, db2.table_relations)
    return matching

def compare_table_relations(rels1, rels2):
    matching = True
    if len(rels1) == len(rels2):
        for rel in rels1:
            rel1 = rels1[rel]
            rel2 = rels2[rel]
            if (rel1['declarative_rel_count'] == rel2['declarative_rel_count'] and
                rel1['other_rel_count'] == rel2['other_rel_count']):
                for d_rel in rel1['declarative_rels']:
                    if d_rel not in rel2['declarative_rels']: 
                        matching = False
                        print('failed in l3')
                for o_rel in rel1['other_rels']:
                    if o_rel not in rel2['other_rels']:
                        matching = False
                        print('failed in l4')
            else: 
                if rel1['total'] == rel2['total']:
                    for d_rel in rel1['declarative_rels']:
                        if d_rel not in rel2['declarative_rels']:
                            if d_rel not in rel2['other_rels']:
                                print(f'REL:{d_rel} moved from declarative to others')
                            else:
                                matching = False
                                print('failed in l5')
                    for o_rel in rel1['other_rels']:
                        if o_rel not in rel2['other_rels']:
                            if o_rel not in rel2['declarative_rels']:
                                print(f'REL:{o_rel} moved from others to declarative')
                            else:
                                matching = False
                                print('failed in l5')
                   
                else:
                    matching = False
                    print('failed in l2')
    else: 
        matching = False
        print('failed in l1')
    return matching

def compare_related_item_ids(relids1, relids2):
    matching = True
    if len(relids1) == len(relids2):
        for relid in relids1:
            relid1 = relids1[relid]
            relid2 = relids2[relid]
            if (len(relid1) == len(relid2)):
                for id in relid1:
                    if id not in relid2:
                        matching = False
                        print(f'failed in l3: for table {relid}, id {id} is missing')
            else:
                matching = False
                print(f'failed in l2: {relid}')
    else:
        matching = False
        print('failed in l1')
    return matching

def set_as_list(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError