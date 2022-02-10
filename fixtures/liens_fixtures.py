from models import LienCopainReunion

liens = [
    LienCopainReunion(
        reunion_id=1, copain_id=1, est_guest=False, dette_active=False, dette=0
    ),
    LienCopainReunion(
        reunion_id=1, copain_id=2, est_guest=False, dette_active=True, dette=1
    ),
    LienCopainReunion(
        reunion_id=1, copain_id=3, est_guest=False, dette_active=False, dette=0
    ),
    LienCopainReunion(
        reunion_id=1, copain_id=4, est_guest=False, dette_active=False, dette=0
    ),
    LienCopainReunion(
        reunion_id=1, copain_id=5, est_guest=True, dette_active=False, dette=0
    ),
]
