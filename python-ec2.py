# Script to automate EC2 with python

import boto
import time

#set the environment variables in the command line:
#    export AWS_ACCESS_KEY_ID=< Your AWS Access Key ID >
#    export AWS_SECRET_ACCESS_KEY=< Your AWS Secret Access Key


# Creating connection object to EC2
#Default login into NA East 1
conn = boto.connect_ec2()

# EC2 Regions
regions = boto.ec2.regions()
print "EC2 Regions :"
print regions
print

# Security Groups
groups = conn.get_all_security_groups()
print "EC2 Security Groups :"
print groups
print


# EC2 Images
images = conn.get_all_images()
print "First of available EC2 Images :"
print images[0]
print images[0].id
print 

#Find the image you are looking for
# This is the latest Ubuntu Natty 11.4 image
# ami-fd589594 - Ubuntu Natty amd64
# ami-e358958a - Ubuntu Natty i386

for image in images:
    if image.id == 'ami-e358958a':
        print "found the image"
        print image.id
        print
        
        myimage=image
    
# Now its time to boot the image
reservation = myimage.run()
print "Booting the machine image"

# The instance is launched
print reservation.instances
print

instance = reservation.instances[0]

#Check the status of the instance
print instance.state
print

start = 0

while instance.state == 'pending':
    print "instance is booting please wait ..."
    time.sleep(5)
    #update instance state
    instance.update()
    start = start + 5

print instance.state
print

print "instance starting time (seconds) : " + str(start)
    
