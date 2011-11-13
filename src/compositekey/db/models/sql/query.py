__author__ = 'aldaran'

from django.core.exceptions import FieldError
from django.db.models.sql.constants import LHS_JOIN_COL, RHS_JOIN_COL, LOOKUP_SEP, LHS_ALIAS
from django.db.models.sql.datastructures import MultiJoin
from django.db.models.sql.query import Query


def add_fields(self, field_names, allow_m2m=True):
    """
    Adds the given (model) fields to the select set. The field names are
    added in the order specified.
    """
    alias = self.get_initial_alias()
    opts = self.get_meta()

    try:
        for name in field_names:
            field, target, u2, joins, u3, u4 = self.setup_joins(
                    name.split(LOOKUP_SEP), opts, alias, False, allow_m2m,
                    True)
            final_alias = joins[-1]
            col = target.column
            cols = col.columns if hasattr(col, "columns") else [col]
            for col in cols:
                if len(joins) > 1:
                    join = self.alias_map[final_alias]
                    if col == join[RHS_JOIN_COL]:
                        self.unref_alias(final_alias)
                        final_alias = join[LHS_ALIAS]
                        col = join[LHS_JOIN_COL]
                        joins = joins[:-1]
                self.promote_alias_chain(joins[1:])
                self.select.append((final_alias, col))
                self.select_fields.append(field)
    except MultiJoin:
        raise FieldError("Invalid field name: '%s'" % name)
    except FieldError:
        names = opts.get_all_field_names() + self.extra.keys() + self.aggregate_select.keys()
        names.sort()
        raise FieldError("Cannot resolve keyword %r into field. "
                "Choices are: %s" % (name, ", ".join(names)))
    self.remove_inherited_models()

add_fields._sign = "monkey patch by compositekey"

def activate_add_fields_monkey_patch():
    # monkey patch
    if not hasattr(Query.add_fields, "_sign"):
        print "activate_add_fields_monkey_patch"
        Query.add_fields = add_fields