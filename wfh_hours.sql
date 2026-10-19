WITH RECURSIVE dates(day) AS (
    SELECT date(MIN(timestamp))
    FROM activity_events

    UNION ALL

    SELECT date(day, '+1 day')
    FROM dates
    WHERE day < date('now', 'localtime')
),
switches AS (
    SELECT
        timestamp,
        CASE
            WHEN message = 'Automation triggered: Switch to Mac'
                THEN 'Mac'
            WHEN message = 'Automation triggered: Switch to PC'
                THEN 'PC'
        END AS destination
    FROM activity_events
    WHERE event_type = 'automation_triggered'
      AND message IN (
          'Automation triggered: Switch to Mac',
          'Automation triggered: Switch to PC'
      )
),
sessions AS (
    SELECT
        timestamp AS mac_start,
        LEAD(timestamp) OVER (ORDER BY timestamp) AS session_end,
        destination
    FROM switches
),
mac_sessions AS (
    SELECT
        mac_start,
        COALESCE(
            session_end,
            datetime('now', 'localtime')
        ) AS mac_end
    FROM sessions
    WHERE destination = 'Mac'
),
daily_hours AS (
    SELECT
        dates.day,
        SUM(
            MAX(
                0,
                (
                    julianday(
                        MIN(mac_sessions.mac_end, datetime(dates.day, '+1 day'))
                    )
                    -
                    julianday(
                        MAX(mac_sessions.mac_start, dates.day)
                    )
                ) * 24
            )
        ) AS hours
    FROM dates
    LEFT JOIN mac_sessions
        ON mac_sessions.mac_start < datetime(dates.day, '+1 day')
       AND mac_sessions.mac_end > dates.day
    GROUP BY dates.day
)
SELECT
    strftime('%d/%m/%Y', day) AS date,
    7.6 AS target,
    ROUND(COALESCE(hours, 0), 2) AS actual
FROM daily_hours
WHERE ROUND(COALESCE(hours, 0), 2) > 0
ORDER BY day;