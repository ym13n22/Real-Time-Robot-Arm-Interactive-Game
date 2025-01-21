using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class fingerMove : MonoBehaviour
{
    // Start is called before the first frame update
    private finger1 f1;
    private finger2 f2;

    private ballMove1 ball1;

    private ballMove2 ball2;

    private ballMove3 ball3;

    private catchedBall cball;

    private effectAppeal effAppl;

    private worningEffects worningeff;

    private AudioSource audioSource;

    private catchedBall catchBall;

    private throwBall thrBall;

    private baseMove bMove;

    public bool enableClose=true;

    private armmove amove;

    

    void Start()
    {
        f1 = FindObjectOfType<finger1>();
        f2 = FindObjectOfType<finger2>();
        ball1 =FindObjectOfType<ballMove1>();
        ball2=FindObjectOfType<ballMove2>();
        ball3=FindObjectOfType<ballMove3>();
        effAppl=FindObjectOfType<effectAppeal>();
        worningeff=FindObjectOfType<worningEffects>();
        cball=FindObjectOfType<catchedBall>();
        audioSource = GetComponent<AudioSource>();
        catchBall=FindObjectOfType<catchedBall>();
        thrBall=FindObjectOfType<throwBall>();
        bMove=FindObjectOfType<baseMove>();
        amove=FindObjectOfType<armmove>();
       // StartCoroutine(MoveAndReturnRoutine()); // 启动协程
    }

    // Update is called once per frame
    void Update()
    {
     
    
     
   
    }

    private IEnumerator MoveAndReturnRoutine()
    {
        moveAction();
        //Debug.Log("Close");
        yield return new WaitForSeconds(5); // 等待5秒
        returnTogether();
        yield return new WaitForSeconds(5); // 等待5秒
        moveAction();
    }

    public void moveTogether(){
     if (enableClose==true){
        f1.catchRotation(10);
        f2.catchRotation(10);
     }
        
    }

    public void returnTogether(){
    float baseRY=0;
    
    float throwtolerance =10f;

    float throwt =15f;

    float armZ=0f;
    if(bMove!=null){
        baseRY=bMove.getRotation();
    }
    //Debug.Log("baseRY "+baseRY);
    if (amove!=null){
        armZ=amove.getRotation();
    }
    Debug.Log("armZ "+armZ);
    if(Mathf.Abs(baseRY - (70)) < throwtolerance&&catchBall.visible==true){
        Debug.Log("Throw ball");
        catchBall.throwBallCatched();
    }
    if(Mathf.Abs(baseRY - (34)) < throwt&&Mathf.Abs(armZ - (320)) < throwtolerance&&catchBall.visible==true){
        Debug.Log("Throw ball");
        catchBall.throwBall();
    }
    else{
        f1.catchRotationBack(10);
        f2.catchRotationBack(10);
    }
        
    }

    public void moveAction(){
    float bllxp1=0;
    float bllxp2=0;
    float bllxp3=0;
    float catchBallX=0;
    float catchBallZ=0;
    float catchBallY=0;
    

    float tolerance =3f;

    float toleranceZ =5f;


    
   
    if(ball1!=null){
      bllxp1= ball1.getXposition();//-0.9
    }
   
    if (ball2!=null){
       bllxp2= ball2.getXposition();//-0.827
    }
    if(ball3!=null){
        bllxp3= ball3.getXposition();//-0.91
    }
    Debug.Log("bllxp1 "+bllxp1+" bllxp2 "+bllxp2+" bllxp3 "+bllxp3);
    if (catchBall != null)
        {
        catchBallX = catchBall.getXposition();
        catchBallZ = catchBall.getZposition();
        catchBallY = catchBall.getYposition();
        }
    //Debug.Log("catchBallX "+catchBallX+" catchBallY "+catchBallY+" catchBallZ "+catchBallZ);
    
    if (Mathf.Abs(catchBallX - (-0.8438723f)) < tolerance &&
        Mathf.Abs(catchBallY - (-0.5594521f)) < tolerance &&
        Mathf.Abs(catchBallZ - 0.03000259f) < tolerance)
        {
        if (-1.2<bllxp1 && bllxp1<-1&&catchBall.visible==false){
        Debug.Log("red ball catched");
        if (effAppl!=null){
        effAppl.startEffect();
        ball1.distoryBall1();
        }
       
    }
    if (-1.2<bllxp2 && bllxp2<-1&&catchBall.visible==false){
        cball.catchBall();
        enableClose=false;
        ball2.distoryBall2();
        //ball3.distoryBall3();
        //if(ball1!=null){
        //ball1.distoryBall1();
        //}
        Debug.Log("green ball catched");
       
    }
    if (-1.2<bllxp3 && bllxp3<-1&&catchBall.visible==false){
        worningeff.worningEffect();
        Debug.Log("yellow ball catched");
    }
    else{
       // Debug.Log("HandColse :"+bllxp3);
       if (audioSource != null)
        {
            audioSource.Play();
        }
        moveTogether();
    }
    }
    else{
        Debug.Log("HandColse :"+bllxp3);
       if (audioSource != null)
        {
            audioSource.Play();
        }
        moveTogether();
    }    
    }
}
