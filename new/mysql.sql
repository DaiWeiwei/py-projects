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