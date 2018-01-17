-- msyql notes

CREATE [TEMPORARY] TABLE [IF NOT EXISTS ] 数据表名
[(create_definition...)][table_option][select_statement]

create_definition:
  col_name
  type
  not null | null
  DEFAULT default_value
  auto_increament
  PRIMARY KEY

ALTER [ignore] TABLE 表名 alter_spec[,alter_spec]...
当指定ignore时，如果出现重复关键的行，则只执行一行，其他重复的行被删除。

alter_specification:
  ADD [COLUMN] create_difinition [FIRST|after column_name]
  ADD index [index_name](index_col_name,...)
  ADD PRIMARY KEY (index_col_name,...)
  ADD  UNIQUE [index_name](index_col_name,...)
  -- ALTER [COLUMN] col_name {SET DEFAULT literral|DROP DEFAULT}
  change [COLUMN] old_col_name create_definition
  modify [COLUMN] create_definition
  DROP [COLUMN] col_name
  DROP PRIMARY KEY
  DROP index index_name
  rename [AS] new_tbl_name
  table_options

RENAME TABLE old to new

DROP TABLE if exists  表名

INSERT INTO table(col1,col2) VALUES (val1, val2)

UPDATE table set col=new_value1 where ...UPDATE

DELETE  FROM table where ...FROM

SELECT .. FROM table1 LEFT|RIGHT join table2 on table1.val = table2.val





