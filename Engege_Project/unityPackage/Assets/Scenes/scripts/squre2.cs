using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class squre2 : MonoBehaviour
{
    private Renderer objectRenderer;

    // Start is called before the first frame update
    void Start()
    {
        // 获取物体的Renderer组件
        objectRenderer = GetComponent<Renderer>();

        // 初始化时将物体隐藏
        if (objectRenderer != null)
        {
            objectRenderer.enabled = false;
        }
        
        // 启动效果
        //startEffect();
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    public void startEffect()
    {
        // 确保物体在调用startEffect时可见
        if (objectRenderer != null)
        {
            objectRenderer.enabled = true;
        }
        
        StartCoroutine(effect());
    }

    public IEnumerator effect()
    {
        // 获取当前物体的初始scale和位置
        Vector3 initialScale = transform.localScale;
        Vector3 initialPosition = transform.position;

        // 在1秒内逐渐改变scale.x从1变为3，同时position.z从0变为10
        float duration = 0.1f;
        float elapsedTime = 0f;

        while (elapsedTime < duration)
        {
            float t = elapsedTime / duration;

            // 将 scale.x 从1变为0.5
            float newScaleX1 = Mathf.Lerp(0f, 0.5f, t);
            transform.localScale = new Vector3(newScaleX1, initialScale.y, initialScale.z);

            

            elapsedTime += Time.deltaTime;
            yield return null;
        }

        // 确保最后的scale.x为0.5
        transform.localScale = new Vector3(0.5f, 3f, initialScale.z);

        // 确保最后的position.z为0
        transform.position = new Vector3(initialPosition.x, initialPosition.y, 0f);
        yield return new WaitForSeconds(0.3f);
        objectRenderer.enabled = false;
    }
}
