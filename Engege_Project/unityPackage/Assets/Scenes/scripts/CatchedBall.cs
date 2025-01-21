using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class catchedBall : MonoBehaviour
{
    public GameObject ballPrefab;
    private Renderer objectRenderer;

    private Rigidbody rb;

    public bool visible;

    private AudioSource audioSource;
    // Start is called before the first frame update
     public float targetY = -3.2f;
    // 物体移动的速度
    public float speed = 10f;

    public float stopHeight = 9.33f;

     public float initialVelocity = 10f; // 初速度
    public float gravity = 9.8f;        // 重力加速度
    public float throwAngle = 45f;      // 投掷角度，单位是度数

    private ballMove2 ball2;

    private fingerMove finm;

    private GameObject newBall;

    private Renderer newBallRenderer;

    public bool ableToCreateNew=true;
    void Start()
    {
        visible=false;
         objectRenderer = GetComponent<Renderer>();

         

         audioSource = GetComponent<AudioSource>();

         

        // 初始化时将物体隐藏
        if (objectRenderer != null)
        {
            objectRenderer.enabled = false;
        }

        ball2=FindObjectOfType<ballMove2>();
        if(ball2==null){
            Debug.Log("ball2 is null");
        }
        finm=FindObjectOfType<fingerMove>();
        if(finm==null){
            Debug.Log("finm is null");
        }
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void catchBall(){
        if (audioSource != null)
        {
            audioSource.Play();
        }
        if (objectRenderer != null)
        {
            objectRenderer.enabled = true;
            visible=true;
            ableToCreateNew=true;
        }
    }
    public float getXposition(){
       return transform.position.x;
    }
    public float getZposition(){
       return transform.position.z;
    }
    public float getYposition(){
       return transform.position.y;
    }
    public void throwBallCatched()
    {
       if (visible==true){
          createNew();
          StartCoroutine(MoveDown());
       }
       
    }

    private void createNew(){
    if (ableToCreateNew){
        newBall = Instantiate(ballPrefab, transform.position, transform.rotation);
         // 获取新球的渲染器
        newBallRenderer = newBall.GetComponent<Renderer>();
        Debug.Log("New ball created");
        newBallRenderer.enabled = true;
        ableToCreateNew=false;
    }
        
    }

    // 协程用于逐渐将物体的y坐标移动到targetY
     private IEnumerator MoveDown()
    { 
        // 获取新球的当前的位置
        Vector3 newBallPosition = newBall.transform.position;
        Debug.Log("new ball position "+newBallPosition);

        // 隐藏原球
        objectRenderer.enabled = false;
        

        // 只要新球的y坐标还没有到达目标位置，就继续移动
        while (newBallPosition.y > targetY)
        {
            newBallRenderer.enabled = true;
            Debug.Log("newBall Down start with "+newBallPosition.y);
            // 计算新的y坐标，使用Mathf.MoveTowards来逐渐接近目标
            float newY = Mathf.MoveTowards(newBallPosition.y, targetY, speed * Time.deltaTime);

            // 设置新球的新位置
            newBall.transform.position = new Vector3(newBallPosition.x, newY, newBallPosition.z);

            // 更新新球的位置
            newBallPosition = newBall.transform.position;


            // 等待下一帧再继续
            yield return null;
        }

        // 当新球到达目标位置后，隐藏新球，并执行后续操作
        newBallRenderer.enabled = false;
        visible = false;
        ball2.redisplayBall2();
        finm.enableClose = true;
    }
    public void throwBall()
    {
       if (visible==true){
          //StartCoroutine(ThrowWithAcceleration());
       }
       
    }

    private IEnumerator ThrowWithAcceleration()
    {
        Vector3 startPosition = transform.position;

        // 计算初始速度的分量
        float throwAngleRad = throwAngle * Mathf.Deg2Rad;
        float initialVelocityX = -initialVelocity * Mathf.Cos(throwAngleRad);
        float initialVelocityY = initialVelocity * Mathf.Sin(throwAngleRad);

        float time = 0;

        while (transform.position.y >= stopHeight)
        {
            time += Time.deltaTime;

            // 计算当前的位置
            float posX = startPosition.x + initialVelocityX * time;
            float posY = startPosition.y + initialVelocityY * time - 0.5f * gravity * time * time;

            transform.position = new Vector3(posX, posY, transform.position.z);

            yield return null; // 等待下一帧
        }
        objectRenderer.enabled = false;

        // 运动结束后可以在这里处理球落地的逻辑
    }

    
}
