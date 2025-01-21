using System.Collections;
using UnityEngine;

public class effectAppeal : MonoBehaviour
{
    private Renderer objectRenderer;
    private AudioSource audioSource;
    // Start is called before the first frame update
    void Start()
    {
        audioSource = GetComponent<AudioSource>();
         if (objectRenderer != null)
        {
            objectRenderer.enabled = false;
        }
        //StartCoroutine(scaleAndMoveEffect());
        //startEffect();
    }
    public void startEffect (){
        StartCoroutine(scaleAndMoveEffect());
    }

    public IEnumerator scaleAndMoveEffect()
    {
        if (audioSource != null)
        {
            audioSource.Play();  // 确保音频源存在，然后播放音效
        }

        if (objectRenderer != null)
        {
            objectRenderer.enabled = true;
        }
        
        // 获取当前物体的初始scale和位置
        Vector3 initialScale = transform.localScale;
        Vector3 initialPosition = transform.position;

        // 在1秒内逐渐改变scale.x从1变为3，同时position.z从0变为10
        float duration = 0.1f;
        float elapsedTime = 0f;

        while (elapsedTime < duration)
        {
            float t = elapsedTime / duration;

            // 将 scale.x 从1变为3
            float newScaleX1 = Mathf.Lerp(1f, 3f, t);
            transform.localScale = new Vector3(newScaleX1, initialScale.y, initialScale.z);

            float newScaleZ1 = Mathf.Lerp(1f, 12f, t);
            transform.localScale = new Vector3(initialPosition.x, initialScale.y, newScaleZ1);


            elapsedTime += Time.deltaTime;
            yield return null;
        }

        // 确保最后的scale.x为3
        transform.localScale = new Vector3(3f, initialScale.y, 12f);

        yield return new WaitForSeconds(0.3f);
        // 物体消失
        Destroy(gameObject);
    }
}
