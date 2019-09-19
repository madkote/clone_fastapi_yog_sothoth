Create diagrams in [WebSequenceDiagrams](https://www.websequencediagrams.com/) app using the following sources:

```
title Matrix Complete Successful Self Registration

User->*+Notification: Complete data registration
Notification->*+Manager: Notification is send to the managers for approval
Manager->*+Registratrion approved: A manager approve the registration
Registratrion approved->*+Matrix registration: Registry is done in Matrix
Matrix registration->*+Registration completed: A random password is generated
Registration completed->+User: The password is send to the user by email
```

```
title Matrix Rejected Self Registration

User->*+Notification: Complete data registration
Notification->*+Manager: Notification is sent to manager for approval
Manager->*+Registration rejected: A manager rejects the registration
Registration rejected->+User: A notification is sent to the user
```

```
title Matrix Failed Self Registration

User->*+Notification: Complete data registration
Notification->*+Manager: Notification is send to the managers for approval
Manager->*+Registration approved: A manager approve the registration
Registration approved->*+Matrix registration: Registry is done in Matrix
Matrix registration->*+Registration failed: An error ocurred
Registration failed->+User: A notification is send to the user
Registration failed->+Manager: A notification is send to the managers
```