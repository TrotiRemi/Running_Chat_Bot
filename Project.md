# Running preparation

    This project is a LLM which help the user to create a personnal running schedule for his goals

## User Data : 
The LLM will first collect the user data to know more about his goal. The data will be collected with questions at the start of the discussion, and them store in the user dataset which the LLM will have at any moment. The data will be : 

- The level of the user (beginner, medium, pro, ect...)
- The goals of the user (a marathon, a trail, a triathlon or other distance)
- deeper information about the user level in running (time in 1km for example or nothing if the user is really a beginner)
- The number of time a week he can run
- Health issue or not
- The time too acheive his goal (for example he has to do a marathon in 8 months)
- Other info (does he has a running 400m place to run, does he has coast close to him)

# Output of the llm

When all the users infos have been stored, the LLM start to propose a schedule of running. The schedule will depend of all the user data and will be accurate because the llm will be train with many other schedules of runnig before.
