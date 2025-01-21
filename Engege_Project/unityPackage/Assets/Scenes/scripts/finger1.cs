using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class finger1 : MonoBehaviour
{
    // 目标旋转角度
    private const float targetRotation = 10f;
    // 每秒旋转的角度
    private const float rotationSpeed = 180f;
    // 累积旋转角度
    private float accumulatedRotation = 0f;

    void Start()
    {
       // catchRotation(10);
    }

    // Update is called once per frame
    void Update()
    {
        // 调用catch方法并传递每帧需要旋转的角度
       
    }

    // Method to rotate the finger along the Z-axis
    public void catchRotation(float rotateAngle)
    {
        if (accumulatedRotation < targetRotation)
        {
            // 每帧旋转的角度
            float rotationThisFrame = rotateAngle;
            
            // 如果加上这一帧的旋转会超过目标角度，则只旋转到目标角度
            if (accumulatedRotation + rotationThisFrame > targetRotation)
            {
                rotationThisFrame = targetRotation - accumulatedRotation;
            }

            // 累计旋转角度
            accumulatedRotation += rotationThisFrame;

            // 获取当前的欧拉角
            Vector3 currentRotation = transform.rotation.eulerAngles;
            // 增加Y轴的旋转
            currentRotation.z += rotationThisFrame;

            // 设置新的旋转
            transform.rotation = Quaternion.Euler(currentRotation);

            //Debug.Log("CurrentRotation is " + currentRotation);
            //Debug.Log("Time.deltaTime is " + Time.deltaTime + " rotationThisFrame is " + rotationThisFrame);
        }
    }

    public void catchRotationBack(float rotationThisFrame)
{
    // 确保我们往回旋转的角度不超过已累积的旋转角度
    if (accumulatedRotation > 0)
    {
        // 如果本帧旋转的角度超过了剩余可旋转角度，则调整为剩余角度
        if (rotationThisFrame > accumulatedRotation)
        {
            rotationThisFrame = accumulatedRotation;
        }

        // 减少累积的旋转角度
        accumulatedRotation -= rotationThisFrame;

        // 获取当前的欧拉角
        Vector3 currentRotation = transform.rotation.eulerAngles;

        // 往回旋转
        currentRotation.z -= rotationThisFrame;

        // 设置新的旋转
        transform.rotation = Quaternion.Euler(currentRotation);

        //Debug.Log("catchRotationBack method called");
        //Debug.Log("CurrentRotation is " + currentRotation);
        //Debug.Log("Time.deltaTime is " + Time.deltaTime + " rotationThisFrame is " + rotationThisFrame);
    }
}

}
