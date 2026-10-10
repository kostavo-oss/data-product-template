-- Fills `squares` from the landed `numbers`: the job's `transform` task, on the warehouse.
-- stevin makes the table (stevin/tables/squares.yml); this only writes its rows, all of
-- them, every run.
-- No catalog and no schema is written here. The job passes them as parameters, by the
-- names the target deployed (resources/*.job.yml).
INSERT OVERWRITE IDENTIFIER(:catalog || '.' || :silver_schema || '.squares')
SELECT
    id,
    square,
    sqrt(square) AS root
FROM IDENTIFIER(:catalog || '.' || :raw_schema || '.numbers')
