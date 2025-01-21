using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class baseMove : MonoBehaviour
{
    // 累计的旋转角度
    public float accumulatedRotation = 0f;
    // 目标旋转角度
    public float targetRotation = 110f;
    // 每秒旋转的角度
    public float rotationSpeed = 180f;

    void Update()
    {
       // rotateY();
       // baseRollBack();
      // SetRotationY(90);
    }

    public void rotateY(float rotateAngle)
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
            currentRotation.y += rotationThisFrame;

            // 设置新的旋转
            transform.rotation = Quaternion.Euler(currentRotation);

            //Debug.Log("CurrentRotation is " + currentRotation);
            //Debug.Log("Time.deltaTime is " + Time.deltaTime + " rotationThisFrame is " + rotationThisFrame);
        }
   
    }
    
    public void SetRotationY(float newYRotation)
    {
        // 获取当前的欧拉角
        Vector3 currentRotation = transform.rotation.eulerAngles;
        // 设置Y轴的旋转值
        currentRotation.y = newYRotation;

        // 设置新的旋转
        transform.rotation = Quaternion.Euler(currentRotation);

        //Debug.Log("New Y Rotation is set to " + newYRotation);
    }



     public void baseRollBack(float rotateAngle)
    {
        if (accumulatedRotation > 0)
        {
            float rotationThisFrame = rotateAngle;
            if (accumulatedRotation - rotationThisFrame < 0)
            {
                rotationThisFrame = accumulatedRotation;
            }
            accumulatedRotation -= rotationThisFrame;
            Vector3 currentRotation = transform.rotation.eulerAngles;
            currentRotation.y -= rotationThisFrame;
            transform.rotation = Quaternion.Euler(currentRotation);

            //Debug.Log("baseRollBack method called");
            //Debug.Log("CurrentRotation is " + currentRotation);
            //Debug.Log("Time.deltaTime is " + Time.deltaTime + " rotationThisFrame is " + rotationThisFrame);
        }
    }
    public float getRotation(){
        return transform.rotation.eulerAngles.y;
    }
}
