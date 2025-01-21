using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class throwBall : MonoBehaviour
{
    private Renderer objectRenderer;
    public float targetY = -3.2f;
    // 物体移动的速度
    public float speed = 10f;
    void Start()
    {
        objectRenderer = GetComponent<Renderer>();
        if (objectRenderer != null)
        {
            objectRenderer.enabled = false;
        }
        
    //down();
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void down()
    {
        if (objectRenderer != null)
        {
            objectRenderer.enabled = true;
        }
        // 启动协程来移动物体
        StartCoroutine(MoveDown());
    }

    // 协程用于逐渐将物体的y坐标移动到targetY
    private IEnumerator MoveDown()
    {
        // 获取物体当前的位置
        Vector3 currentPosition = transform.position;

        // 只要物体的y坐标还没有到达目标位置，就继续移动
        while (currentPosition.y > targetY)
        {
            // 计算新的y坐标，使用Mathf.MoveTowards来逐渐接近目标
            float newY = Mathf.MoveTowards(currentPosition.y, targetY, speed * Time.deltaTime);

            // 设置物体的新位置
            transform.position = new Vector3(currentPosition.x, newY, currentPosition.z);

            // 更新当前的位置
            currentPosition = transform.position;

            // 等待下一帧再继续
            yield return null;
        }
    }
}
