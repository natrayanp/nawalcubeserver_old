def get_status(curstatus,newstatus,curreason, newreason):
    '''
    status =   
                -3 --> success
                -1 --> warning for which program flow not to be stopped
                0 --> empty
                1  --> data error
                2  --> db error
                3  --> both data and db error
    '''
    print(curstatus,newstatus,curreason, newreason)
    if curstatus == None:
        curstatus = -1

    setstatus = -1
    
    if newstatus == -3:
        setstatus = -3
        setreason = None
    else:
        if curstatus < 0:
            setstatus = newstatus
        elif curstatus == 2:
            setstatus = curstatus
        elif curstatus == newstatus:
            setstatus = curstatus
        elif curstatus != newstatus:
            setstatus = 2

        if curreason and setstatus > -1:
            setreason = curreason + " | " + newreason
        else:
            setreason = newreason

    return -1 if setstatus == None else setstatus, setreason