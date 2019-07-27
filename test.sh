#!/bin/bash

# Test functions for Comodiac

# Add target
comodiac add-target -v -c test -t this.com,127.0.0.1,that.com,one.more.domain,*.that.com

# View the first schedule
comodiac view-schedule -S 1

# Add schedule
comodiac add-schedule -c test -t test.com -T ping_check -v

# Run the 'heartbeat' - normally performed by a cron job.
comodiac heartbeat
