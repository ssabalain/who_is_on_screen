with boundaries as (

  select
    actor,
    is_start,
    frame_number as frame_number_from,
    timestamp as timestamp_from,

    cast(
      lead(frame_number) over(
        partition by actor
        order by frame_number
      ) as int
    ) as frame_number_to,

    lead(timestamp) over(
      partition by actor
      order by frame_number
    ) as timestamp_to

  from short_timeline

),

aggregated_calculations as (

  select
    full_timeline.*,

    frame_number_from,
    timestamp_from,
    frame_number_to,
    timestamp_to,

    case
      when boundaries.actor is not null then true
      else false
    end as is_bunch,

    case
      when boundaries.actor is not null
        then count(*) over(
          partition by full_timeline.actor, frame_number_from
        )
    end as length,

    case
      when boundaries.actor is not null
        then max(pred_value) over(
          partition by full_timeline.actor, frame_number_from
        )
    end as max_pred_value,

    case
      when boundaries.actor is not null
        then sum(pred_value) over(
          partition by full_timeline.actor, frame_number_from
        )
    end as sum_pred_value

  from full_timeline
  left join boundaries on full_timeline.actor = boundaries.actor
    and full_timeline.frame_number between boundaries.frame_number_from and boundaries.frame_number_to
    and boundaries.is_start
  order by actor, frame_number

)

select
    actor,
    frame_number_from,
    timestamp_from,
    frame_number_to,
    timestamp_to,
    length,
    max_pred_value,
    sum_pred_value

from aggregated_calculations
where is_bunch
group by 1,2,3,4,5,6,7,8