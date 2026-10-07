-- What people query: shaped from raw. A table, by dbt_project.yml; a model can say
-- otherwise with a config() block at its top. Mind that dbt reads Jinja in comments too.
select
    id,
    square,
    sqrt(square) as root
from {{ source('raw', 'numbers') }}
