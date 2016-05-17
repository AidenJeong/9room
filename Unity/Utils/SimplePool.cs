using UnityEngine;
using System.Collections;
using System.Collections.Generic;

public static class SimplePool {

    const int DEFAULT_POOL_SIZE = 5;
    
    static public Transform hidePosition
    {
        get; set;
    }

    class Pool
    {
        int nextId = 1;
        GameObject prefab;
        Stack<GameObject> inactive;

        public Pool(GameObject prefab, int initCount)
        {
            this.prefab = prefab;
            inactive = new Stack<GameObject>(initCount);
        }

        public GameObject DefaultObject()
        {
            Vector3 pos;
            if (hidePosition == null)
                pos = new Vector3(-10, 0, 0);
            else
                pos = hidePosition.position;

            GameObject obj = UnityEngine.Object.Instantiate(
                prefab,
                pos,
                Quaternion.identity) as GameObject;

            return obj;
        }

        public GameObject CreateNewObject()
        {
            GameObject obj;

            obj =  DefaultObject();

            obj.name = prefab.name + " (" + (nextId++) + ")";
            obj.AddComponent<PoolMember>().myPool = this;
            obj.SetActive(false);

            return obj;
        }

        public GameObject Spawn(Vector3 pos)
        {
            GameObject obj;
            if (inactive.Count == 0)
            {
                obj = CreateNewObject();
            }
            else
            {
                obj = inactive.Pop();
                if (obj == null)
                {
                    return Spawn(pos);
                }
            }

            obj.transform.position = pos;
            obj.SetActive(true);

            return obj;
        }

        public void Despawn(GameObject obj)
        {
            obj.SetActive(false);

            if (hidePosition != null)
                obj.transform.position = hidePosition.position;

            inactive.Push(obj);
        }

        public void Purge()
        {
            while (inactive.Count != 0)
            {
                GameObject obj = inactive.Pop();
                GameObject.Destroy(obj);
            }

            inactive.Clear();
        }
    }

    class PoolMember : MonoBehaviour
    {
        public Pool myPool;
    }

    static Dictionary<GameObject, Pool> pools;

    static public void Init(
        GameObject prefab = null, 
        int qty = DEFAULT_POOL_SIZE)
    {
        if (pools == null)
            pools = new Dictionary<GameObject, Pool>();

        if (prefab != null && pools.ContainsKey(prefab) == false)
            pools[prefab] = new Pool(prefab, qty);
    }

    static public void Preload(GameObject prefab, int qty = 1)
    {
        Init(prefab, qty);

        Vector3 pos = Vector3.zero;
        if (hidePosition != null)
            pos = hidePosition.position;

        GameObject[] obj = new GameObject[qty];
        for (int i = 0; i < qty; ++i)
            obj[i] = Spawn(prefab, pos);

        for (int i = 0; i < qty; ++i)
            Despawn(obj[i]);
    }

    static public GameObject Spawn(GameObject prefab, Vector3 pos)
    {
        Init(prefab);
        return pools[prefab].Spawn(pos);
    }

    static public void Despawn(GameObject obj)
    {
        PoolMember pm = obj.GetComponent<PoolMember>();
        if (pm == null)
        {
            Debug.Log("Object '" + obj.name + "' wasn't spawned from a pool. Destroying it instead.");
            GameObject.Destroy(obj);
        }
        else
        {
            pm.myPool.Despawn(obj);
        }
    }

    static public void Purge()
    {
        foreach (Pool pool in pools.Values)
            pool.Purge();
        pools.Clear();
    }
}
