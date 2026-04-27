create database internship_prog_project_4
use internship_prog_project_4
--------------------------TABLES-------------------------------------
select * from customers
select * from delivery_events
select * from driver_monthly_metrics
select * from drivers         --null present
select * from facilities      
select * from fuel_purchases  --null present
select * from loads
select * from maintenance_records
select * from routes
select * from safety_incidents --null present
select * from trailers
select * from trips           --null present
select * from truck_utilization_metrics
select * from trucks


--------------------Duplicate CHECKING----------------------------
--customers
select count( *) from customers
select distinct * from customers
--no duplicate


--delivery_events
select count( *) from delivery_events
select distinct * from delivery_events
--no duplicate row exist


--driver_monthly_metrics
select count( *) from driver_monthly_metrics
select  distinct * from driver_monthly_metrics
--no duplicate row exist


--drivers
select count( *) from drivers
select  distinct * from drivers
--no duplicate row exist


--facilities
select count( *) from facilities
select  distinct * from facilities
--no duplicate row exist


--fuel_purchases
select count( *) from fuel_purchases
select  distinct * from fuel_purchases
--no duplicate row exist


--loads
select count( *) from loads
select  distinct * from loads
--no duplicate row exist


--maintenance_records
select count( *) from maintenance_records
select  distinct * from maintenance_records
--no duplicate row exist


--routes
select count( *) from routes
select  distinct * from routes
--no duplicate row exist


--safety_incidents
select count( *) from safety_incidents
select  distinct * from safety_incidents
--no duplicate row exist


--trailers
select count( *) from trailers
select  distinct * from trailers
--no duplicate row exist


--trips
select count( *) from trips
select  distinct * from trips
--no duplicate row exist


--truck_utilization_metrics
select count( *) from truck_utilization_metrics
select  distinct * from truck_utilization_metrics
--no duplicate row exist


--trucks
select count( *) from trucks
select  distinct * from trucks
--no duplicate row exist

;with cte_1 as (
select *,DENSE_RANK()over (partition by truck_id  order by truck_id )  rnk from trucks
)
select * from cte_1
where  rnk=2


-----------------------NULLS CHECKING------------------------
--customers
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('customers');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM customers;';

EXEC sp_executesql @sql;



--delivery_events
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('delivery_events');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM delivery_events;';

EXEC sp_executesql @sql;


--driver_monthly_metrics
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('driver_monthly_metrics');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM driver_monthly_metrics;';

EXEC sp_executesql @sql;

--drivers
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('drivers');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM drivers;';

EXEC sp_executesql @sql;
--found 124 null values in termination_date column


--facilities
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('facilities');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM facilities;';

EXEC sp_executesql @sql;


--fuel_purchases
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('fuel_purchases');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM fuel_purchases;';

EXEC sp_executesql @sql;
--found 3880 and 3988 null values in truck_id and driver_id columns respectively.


--loads
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('loads');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM loads;';

EXEC sp_executesql @sql;

--maintenance_records
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('maintenance_records');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM maintenance_records;';

EXEC sp_executesql @sql;

--routes
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('routes');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM routes;';

EXEC sp_executesql @sql;

--safety_incidents
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('safety_incidents');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM safety_incidents;';

EXEC sp_executesql @sql;
--found 1 null value in trip_id and driver_id


--trailers
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('trailers');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM trailers;';

EXEC sp_executesql @sql;

--trips
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('trips');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM trips;';

EXEC sp_executesql @sql;
--found 1714,1672,1680 null values in driver_id,truck_id,trailer_id respectively.


--truck_utilization_metrics
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('truck_utilization_metrics');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM truck_utilization_metrics;';

EXEC sp_executesql @sql;

--trucks
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 
'SUM(CASE WHEN ' + QUOTENAME(name) + ' IS NULL THEN 1 ELSE 0 END) AS ' + QUOTENAME(name + '_nulls') + ','
FROM sys.columns
WHERE object_id = OBJECT_ID('trucks');

SET @sql = 'SELECT ' + LEFT(@sql, LEN(@sql)-1) + ' FROM trucks;';

EXEC sp_executesql @sql;

------------------------------------------OBSERVATIONS--------------------------------
--XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
----------------------------------------CUSTOMERS-------------------------------------
--one customer can place more than one load
select customer_id,count(load_id)as total_loads from loads
group by customer_id

--account_status = 'Inactive' but loads still created---who placed btw--2020-01-09--2021-12-11
select min(contract_start_date),max(contract_start_date) from customers as c inner join loads l 
on c.customer_id=l.customer_id
where account_status='inactive'

--date checking(2 years of customers data)--2020-01-07---2022-01-01
select min(contract_start_date),max(contract_start_date) from customers

--data is available for 2 years--2022-01-01--2024-12-31
select min(load_date),max(load_date) from loads

--no customerid which is not present in loads
select customer_id from customers 
where customer_id not in (select customer_id from loads )

--xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx---
-------------------------------------LOADS-------------------------------------------------------
select * from loads
--NO LOAD date is less than contract start date
select * from loads l inner join customers c 
on l.customer_id=c.customer_id
where l.load_date> c.contract_start_date

--Each load is associated with only one trip.
select load_id,count(trip_id) as total_trip from trips
group by load_id

--same dispatch and load date
select * from trips t inner join loads l
on t.load_id=l.load_id
where t.dispatch_date != l.load_date

--there is no such record with Revenue = 0 but trip completed
select * from loads as l inner join trips as t
on l.load_id=t.load_id
where revenue =0 and trip_status='Completed'

--xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx---
---------------------------------TRIPS--------------------------------------------------
SELECT * from trips
--
select trip_id,count(event_id) all_events from delivery_events
group by trip_id

select * from delivery_events as d
inner join loads l 
on d.load_id=l.load_id
inner join customers c 
on c.customer_id=l.customer_id
where trip_id='TRIP00006335'





--Some trips do not have driver and truck details recorded, so the same information is also missing
--in related tables like fuel purchases..
select * from fuel_purchases f
join trips t on f.trip_id = t.trip_id --and f.driver_id=t.driver_id
where f.truck_id is null or f.driver_id is null;


--Drivers 
select * from drivers
where termination_date is not null and employment_status='Active'

--fuel_purchases
select trip_id from fuel_purchases where trip_id not in (select trip_id  from trips)
select * from trips

--some trip ids are not present in fuel purchases table--8471
select trip_id from trips where trip_id not in (select trip_id  from fuel_purchases)

--fuel_gallons_used = 0 but trip completed ❌
select * from trips 
where fuel_gallons_used=0 and trip_status='Completed'

--average_mpg = 200 ❌
select * from trips 
where average_mpg=200 

--distance = negative ❌
select * from trips 
where actual_distance_miles<0

--detention_minutes < 0 ❌
select * from delivery_events
where detention_minutes<0







-- Check distance
select avg(actual_distance_miles)
from trips
where trailer_id is null and trip_status='Completed';

--One trip assigned two drivers at same time ❌
SELECT trip_id,dispatch_date,COUNT(DISTINCT driver_id) AS driver_count FROM trips
GROUP BY trip_id, dispatch_date
HAVING COUNT(DISTINCT driver_id) > 1;



--trip has truck_id not in Trucks
select truck_id from trips 
where truck_id not in (select truck_id from trucks)

--incident has driver_id not in Drivers
select driver_id from safety_incidents
where driver_id not in(select driver_id from drivers)

--







--------------------------data inconsistencies--------------------------------
--1,680 completed trips have a load assigned but are missing trailer information, indicating a data quality gap.
select * from trips 
where trailer_id is null and load_id is not null and trip_status='Completed'


--Same truck in two trips at same time
SELECT truck_id,dispatch_date,COUNT(DISTINCT trip_id) AS trip_count FROM trips
WHERE truck_id IS NOT NULL
GROUP BY truck_id, dispatch_date
HAVING COUNT(DISTINCT trip_id) > 1;


select * from trips 
where truck_id='TRK00053' and dispatch_date='2023-06-21'


--Same driver on overlapping trips
SELECT a.driver_id,a.trip_id AS trip_1,b.trip_id AS trip_2
FROM trips a
JOIN trips b
  ON a.driver_id = b.driver_id
 AND a.trip_id < b.trip_id  -- avoid self-join duplicates
 AND a.dispatch_date = b.dispatch_date  -- same dispatch date
ORDER BY a.driver_id, a.trip_id;

--Truck utilization > 100% 
select * from truck_utilization_metrics
where utilization_rate>1.00


--------------------------------Data Cleaning-------------------------------------------
--for trips,fuel_purchses,safety_incidents tables
select * into fuel_purchases_copy from fuel_purchases
select * into trips_copy from trips
select * into safety_incidents_copy from safety_incidents


UPDATE fuel_purchases
SET 
driver_id = COALESCE(driver_id, 'Not Assigned'),
truck_id  = COALESCE(truck_id, 'Not Assigned');


UPDATE trips
SET 
driver_id = COALESCE(driver_id, 'Not Assigned'),
truck_id  = COALESCE(truck_id, 'Not Assigned'),
trailer_id  = COALESCE(trailer_id, 'Not Assigned')

UPDATE safety_incidents
SET 
driver_id = COALESCE(driver_id, 'Not Assigned'),
truck_id  = COALESCE(truck_id, 'Not Assigned')


select * from delivery_events
select (actual_datetime)-(scheduled_datetime) from delivery_events


select truck_id from (
select truck_id from trucks
where truck_id not in(select truck_id from truck_utilization_metrics)
) x
where truck_id in (select truck_id from trips)

select * from trips
where truck_id='TRK00003'


select distinct truck_id from truck_utilization_metrics
where truck_id not in (select truck_id from trips)

select  * from truck_utilization_metrics
where truck_id='TRK00031'and year(month)=2022

select * from trips
where truck_id='TRK00031' and year(dispatch_date)=2022
group by truck_id
having year(dispatch_date)=2020

;with cte1 as(
select truck_id, sum(trips_completed) trips_completed from truck_utilization_metrics
group by truck_id
),
cte2 as(
select truck_id as truck,COUNT(trip_id) trips from trips
group by truck_id
),
cte3 as(
select * from cte1 t inner join cte2 p
on t.truck_id =p.truck
)
select * from cte3
where trips_completed<>trips

select count(*)*1.0/(select count(* ) from trips) *100 from (
select * from trips
WHERE truck_id ='Not Assigned') x

select *  from truck_utilization_metrics tu
left join trucks t
on tu.truck_id=t.truck_id


select sum(fuel_surcharge)fuel_surcharge,sum(total_cost)fuel_total_cost,(sum(total_cost) - sum(fuel_surcharge)) from loads l inner join trips t
on l.load_id=t.load_id
inner join fuel_purchases as f 
on t.trip_id=f.trip_id

SELECT *FROM (
SELECT t.trip_id,e.on_time_flag,
CASE WHEN scheduled_datetime < actual_datetime THEN 0
ELSE 1
        END AS calculated_on_time
    FROM trips t
    LEFT JOIN delivery_events e
        ON t.trip_id = e.trip_id
) x
WHERE calculated_on_time <> on_time_flag;
SELECT * FROM delivery_events
WHERE trip_id='TRIP00000006'


--total fuel cost
SELECT 
    SUM(total_cost) AS total_fuel_cost
FROM fuel_purchases;

--total maintenance cost
SELECT 
    SUM(total_cost) AS total_maintenance_cost
FROM maintenance_records;

--total incident cost
SELECT 
    SUM(
        COALESCE(claim_amount,0) 
      + COALESCE(vehicle_damage_cost,0) 
      + COALESCE(cargo_damage_cost,0)
    ) AS total_incident_cost
FROM safety_incidents;

---
WITH revenue_cte AS (
    SELECT SUM(revenue) AS total_revenue
    FROM loads
    WHERE load_status = 'Completed'
),

fuel_cte AS (
    SELECT SUM(total_cost) AS total_fuel_cost
    FROM fuel_purchases
),

maintenance_cte AS (
    SELECT SUM(total_cost) AS total_maintenance_cost
    FROM maintenance_records
),

incident_cte AS (
    SELECT SUM(
            COALESCE(claim_amount,0) 
          + COALESCE(vehicle_damage_cost,0) 
          + COALESCE(cargo_damage_cost,0)
        ) AS total_incident_cost
    FROM safety_incidents
)

SELECT
    r.total_revenue,
    f.total_fuel_cost,
    m.total_maintenance_cost,
    i.total_incident_cost,

    -- Total Cost
    (f.total_fuel_cost 
     + m.total_maintenance_cost 
     + i.total_incident_cost) AS total_cost,

    -- Gross Profit
    (r.total_revenue 
     - (f.total_fuel_cost 
        + m.total_maintenance_cost 
        + i.total_incident_cost)) AS gross_profit,

    -- Profit Margin %
    ROUND(
        (r.total_revenue 
         - (f.total_fuel_cost 
            + m.total_maintenance_cost 
            + i.total_incident_cost)
        ) 
        / r.total_revenue * 100, 2
    ) AS profit_margin_percent

FROM revenue_cte r
CROSS JOIN fuel_cte f
CROSS JOIN maintenance_cte m
CROSS JOIN incident_cte i;


--
SELECT 
    ROUND(AVG(CAST(on_time_flag AS FLOAT)) * 100, 2) 
    AS on_time_delivery_percent
FROM delivery_events;
--
SELECT 
    ROUND(
        SUM(actual_distance_miles) * 1.0 
        / SUM(fuel_gallons_used),
        2
    ) AS fleet_mpg
FROM trips
WHERE trip_status = 'Completed';

--
SELECT 
    ROUND(
        SUM(fp.total_cost) * 1.0 
        / SUM(t.actual_distance_miles),
        2
    ) AS fuel_cost_per_mile
FROM fuel_purchases fp
JOIN trips t ON fp.trip_id = t.trip_id
WHERE t.trip_status = 'Completed';


--
SELECT 
    ROUND(
        COUNT(si.incident_id) * 100.0 
        / COUNT(DISTINCT t.trip_id),
        2
    ) AS incident_rate_percent
FROM trips t
LEFT JOIN safety_incidents si 
    ON t.trip_id = si.trip_id
WHERE t.trip_status = 'Completed';

--
SELECT 
    ROUND(AVG(detention_minutes), 2) 
        AS avg_detention_minutes
FROM delivery_events;

--
SELECT 
    ROUND(
        SUM(l.revenue) * 1.0 
        / SUM(t.actual_distance_miles),
        2
    ) AS revenue_per_mile
FROM loads l
JOIN trips t ON l.load_id = t.load_id
WHERE t.trip_status = 'Completed';

--
SELECT 
    ROUND(AVG(CAST(downtime_hours AS FLOAT)), 2) AS avg_downtime_hours
FROM maintenance_records;



select day(dispatch_date),count(trip_id) from trips
group by day(dispatch_date)
order by day(dispatch_date)

select * from facilities

