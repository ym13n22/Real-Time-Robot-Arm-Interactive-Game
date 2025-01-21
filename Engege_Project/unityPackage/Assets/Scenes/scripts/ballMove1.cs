using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ballMove1 : MonoBehaviour
{
    // 球体平移速度
    public float speed = 5.0f;

    // 超过此值后球体将从右边重新出现
    public float leftBoundary = -2.0f;
    public float rightBoundary = 7.0f;

    // Update is called once per frame
    void Update()
    {
        // 每帧更新球体的x轴位置
        transform.Translate(Vector3.left * speed * Time.deltaTime);

        // 如果球体的x位置超出了左边界
        if (transform.position.x < leftBoundary)
        {
            // 将球体的位置设置到右边界
            transform.position = new Vector3(rightBoundary, transform.position.y, transform.position.z);
        }
    }

    public float getXposition(){
       return transform.position.x;
    }
    public void distoryBall1(){
        transform.localScale = Vector3.zero;
    }
}
