with pred_values as (

  select
    '{0}' as actor,
    frame_number,
    frames_df.timestamp,

    case
        when pred_1_name like '%{0}%' then coalesce(pred_1_value,0)
        else 0
    end as pred_1_value,

    case
        when pred_2_name like '%{0}%' then coalesce(pred_2_value,0)
        else 0
    end as pred_2_value

  from frames_df
  left join results_df using(frame_number)

),

aux_fields as (

  select
    actor,
    frame_number,
    timestamp,
    pred_1_value,
    pred_2_value,

    case
        when (pred_1_value != 0 or pred_2_value != 0) then 1
        else 0
    end as has_value

  from pred_values

),

flag as (

  select
    *,

    case
        when sum(has_value) over (order by frame_number rows between 3 PRECEDING and 3 following) > 1 then true
        else false
    end as is_part_of_sequence

  from aux_fields

),

preeliminar_predictions as (

  select
    actor,
    frame_number,
    timestamp,

    case
        when is_part_of_sequence and pred_1_value = 0
            then sum(pred_1_value) over (order by frame_number rows between current row and 2 following)
        when is_part_of_sequence then pred_1_value
        else 0
    end as pred_1_value,

    case
        when is_part_of_sequence and pred_2_value = 0
            then sum(pred_2_value) over (order by frame_number rows between current row and 2 following)
        when is_part_of_sequence then pred_2_value
        else 0
    end as pred_2_value

  from flag

),

final_prediction as (

  select
    actor,
    frame_number,
    timestamp,

    case
        when pred_1_value !=0 then pred_1_value
        when pred_2_value !=0 then pred_2_value
        else 0
    end as pred_value

  from preeliminar_predictions

),

start_end_flags as (

  select
    *,

    case
        when lag(pred_value) over (order by frame_number) = 0 and pred_value != 0 then true
        else false
    end as is_start,

    case
        when lead(pred_value) over (order by frame_number) = 0 and pred_value != 0 then true
        else false
    end as is_end

  from final_prediction

)

select * from start_end_flags
where {1}