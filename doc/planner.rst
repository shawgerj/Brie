.. _planner:

*******
Planner
*******
The planner and the calendar are essentially the same thing. They both use the same tastypie + backbone + FullCalendar structure. The planner, however, displays PlannerBlock models instead of Shift models. Backbone.js must be configured to pull its data from the ``planner_block`` API instead of the ``shift`` API. All of the code for this is in ``/static/js/planner_cal_app.js``. PlannerBlocks can have three different states -- preferred, unavailable, or in class. They are shown as different colors depending on their state.

The planner also only shows a single, fixed week. This makes it easy for conleaders to compare planners from everybody in their lab. Dates are not important at all -- really the best solution would be to have a date-less calendar that just showed a week. 
