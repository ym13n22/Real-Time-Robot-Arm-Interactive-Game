using UnityEngine;

public class ScaleOverTime : MonoBehaviour
{
    public float speed = 0.2f; 
    public float maxScaleX = 1f; // 最大的 scale.x 值

    private float currentScaleX = 0f; // Accumulated scale value

    void Update()
    {
        // Update the scale over time
        UpdateScale();
    }

    void UpdateScale()
    {
        //Debug.Log("currentScale "+currentScaleX);
        if (currentScaleX < maxScaleX)
        {
            //Debug.Log("Increase");
            // Incrementally increase the current scale
            currentScaleX += Time.deltaTime * speed;

            // Clamp the scale to ensure it does not exceed maxScaleX
            if (currentScaleX >= maxScaleX)
            {
                currentScaleX = maxScaleX;
                Time.timeScale = 0f;
            }

            // Apply the updated scale to the transform
            transform.localScale = new Vector3(currentScaleX, transform.localScale.y, transform.localScale.z);
        }
    }
}

