new_types = ['int1', 'uint1', 'uint2', 'uint4', 'uint8']
old_types = ['int2', 'int4', 'int8']

op_words = {'<': 'lt', '<=': 'le', '=': 'eq', '<>': 'ne', '>=': 'ge', '>': 'gt'}

c_types = {
    'int1': 'int8',
    'int2': 'int16',
    'int4': 'int32',
    'int8': 'int64',
    'uint1': 'uint8',
    'uint2': 'uint16',
    'uint4': 'uint32',
    'uint8': 'uint64',
}

f_compare_c = open('compare.c', 'w')
f_compare_sql = open('compare.sql', 'w')
f_test_compare_sql =  open('test/sql/compare.sql', 'w')

f_compare_c.write('#include <postgres.h>\n')
f_compare_c.write('#include <fmgr.h>\n\n')
f_compare_c.write('#include "uint.h"\n\n')

for leftarg in new_types + old_types:
    for rightarg in new_types + old_types:
        if leftarg in old_types and rightarg in old_types:
            continue
        for op in ['<', '<=', '=', '<>', '>=', '>']:
            funcname = leftarg + rightarg + op_words[op]
            f_compare_c.write("""
PG_FUNCTION_INFO_V1(%s);
Datum
%s(PG_FUNCTION_ARGS)
{
	%s arg1 = PG_GETARG_%s(0);
	%s arg2 = PG_GETARG_%s(1);

	PG_RETURN_BOOL(arg1 %s arg2);
}
""" % (funcname, funcname,
       c_types[leftarg], c_types[leftarg].upper(),
       c_types[rightarg], c_types[rightarg].upper(),
       op if op != '<>' else '!='))
            f_compare_sql.write("""
CREATE FUNCTION %s(%s, %s) RETURNS boolean IMMUTABLE LANGUAGE C AS '$libdir/uint', '%s';

CREATE OPERATOR %s (
    PROCEDURE = %s,
    LEFTARG = %s,
    RIGHTARG = %s
);
""" % (funcname, leftarg, rightarg, funcname,
       op, funcname, leftarg, rightarg))
            f_test_compare_sql.write("SELECT '1'::%s %s '1'::%s;\n" % (leftarg, op, rightarg))
            f_test_compare_sql.write("SELECT '5'::%s %s '2'::%s;\n" % (leftarg, op, rightarg))
            f_test_compare_sql.write("SELECT '3'::%s %s '4'::%s;\n" % (leftarg, op, rightarg))

        f_test_compare_sql.write("\n")

f_compare_c.close()
f_compare_sql.close()
f_test_compare_sql.close()
