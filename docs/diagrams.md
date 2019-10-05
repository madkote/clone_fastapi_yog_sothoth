Create diagrams in [WebSequenceDiagrams](https://www.websequencediagrams.com/) app using the following sources:

```
title Matrix Complete Successful/Failed Self Registration

User->*+Yog-Sothoth: Request w/ optional email
Yog-Sothoth->*+Manager: Notify
Yog-Sothoth->+User: Notify
Manager->+Yog-Sothoth: Approves
Yog-Sothoth->+Manager: Notify
Yog-Sothoth->+User: Notify
User->+Yog-Sothoth: Create account
Yog-Sothoth->*+Matrix: Create account
Matrix->+Yog-Sothoth: Succesfull/failed
Yog-Sothoth->+Manager: Notify
Yog-Sothoth->+User: Notify
```

```
title Matrix Rejected Self Registration

User->*+Yog-Sothoth: Request w/ optional email
Yog-Sothoth->*+Manager: Notify
Yog-Sothoth->+User: Notify
Manager->+Yog-Sothoth: Rejects
Yog-Sothoth->+Manager: Notify
Yog-Sothoth->+User: Notify
```

```
title Matrix Delete Self Yog-Sothoth (before approval)

User->*+Yog-Sothoth: Request w/ optional email
Yog-Sothoth->*+Manager: Notify
Yog-Sothoth->+User: Notify
User->+Yog-Sothoth: Delete request
```

```
title Matrix Delete Self Yog-Sothoth (after approval)

User->*+Yog-Sothoth: Request w/ optional email
Yog-Sothoth->*+Manager: Notify
Yog-Sothoth->+User: Notify
Manager->+Yog-Sothoth: Approves
Yog-Sothoth->+Manager: Notify
Yog-Sothoth->+User: Notify
User->+Yog-Sothoth: Delete request
```
