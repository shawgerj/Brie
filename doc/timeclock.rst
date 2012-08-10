.. _timeclock:

*********
Timeclock
*********


TimeclockActions
================
Model::

    class TimeclockAction(models.Model):
	time = models.DateTimeField()
	IP = models.IPAddressField()
	employee = models.ForeignKey(User)

When a user presses the "clock in" link, ricotta checks to see if they are already clocked in. If not, a TimeclockAction is created with the time of clockin and the IP address of the computer they are using. If they are clocked in already (if a TimeclockAction belonging to their user already exists), delete the existing TimeclockAction and create a TimeclockRecord.

TimeclockRecords
================
TimeclockRecords are like two TimeclockActions in one model.::

    class TimeclockRecord(models.Model):
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()
	inIP = models.IPAddressField()
	outIP = models.IPAddressField()
	employee = models.ForeignKey(User)

They record the start and end times, and in and out IPs of an employee's clock-in period.

Views
=====
There are a number of views associated with timeclocks. Employees can view their own timeclocks at ``/timeclock/<username>``. Timeclock records from the current pay period are shown. Users can view other pay periods by clicking the back and forward links at the bottom of the page. A simple table is shown with all the information from the model, and an additional column showing the "Kronos Time". Kronos time is the duration of the shift in hours in decimal form. So for example, two and half hours would be 2.5. One hour and 45 minutes would be 1.75. This is the number that employees should copy into their Kronos timesheet for that day. At the bottom of the view are the total hours clocked, and the total hours scheduled (both in Kronos time units). If there is a serious discrepancy in these numbers, it may alert the employee that at least one of their timeclock records is incorrect.

Conleaders have access to the timeclock cumulative view. It is a table showing each employee, and their total clocked and scheduled hours. For more details, conleaders may click on an employee's username to view their complete timeclock history. Using this view, conleaders may quickly check for discrepancies between employee's clocked and scheduled hours.

Future Work
===========
As of this writing, the timeclock does not interact with the calendar at all. When a user clocks in or out, ricotta should check against that user's shifts and ensure that they are performing a timeclock action within a given time window of their shift. Otherwise, a warning should be displayed, or they should not be able to clock in. Warnings should also be showed on the conleader's global timeclock view for users with discrepancies between their timeclock records and their shift records. 

The IP address is sort of broken. Fix it and use it to match against known location IPs. Clock-in attempts from unrecognized locations may be blocked.
