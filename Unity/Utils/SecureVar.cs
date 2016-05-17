using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using _uint64 = System.UInt64;


namespace NMSGuard
{
    static class Constants
    {
        public const int STRG_COL_NUM   = 15;
        public const int STRG_LOW_NUM   = 20;
        public const int INVALID_INDEX  = -1;
        public const int  CHUNK_NUM     = 5;         
    }

    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //
    //  create random value - WELL512 사용 : 성능 ok.. state 테이블의 메모리 조작 또는 고정이 되어도 상관없음
    //
    public class WellRng
    {   
        private const int WELLRNG512_TB_NUM = 16;
        private static uint _index = 0;

        // initialize state to random bits
        private static uint[] _state = new uint[WELLRNG512_TB_NUM] {
	        0x18b74777, 0x88085ae6, 0xff0f6a70, 0x66063bca,
	        0x8f659eff, 0xf862ae69, 0x616bffd3, 0x166ccf45,
	        0xd70dd2ee, 0x4e048354, 0x3903b3c2, 0xa7672661,
	        0x4969474d, 0x3e6e77db, 0xaed16a4a, 0xd9d65adc
        };

        public WellRng()
        {    
        }

        public static void WELLINIT()
        {
            Random r = new Random();
            _index = (uint)r.Next(0, WELLRNG512_TB_NUM);
        }
  
        // return 32 bit random number
        //
        public static uint WELLRNG512( )
        {
	        uint a, b, c, d;
	        a = _state[_index];
	        c = _state[(_index+13)&15];
	        b = a^c^(a<<16)^(c<<15);
	        c = _state[(_index+9)&15];
	        c ^= (c>>11);
	        a = _state[_index] = b^c;
	        d = a^((a<<5)&0xDA442D20);
	        _index = (_index + 15)&15;
	        a = _state[_index];
	        _state[_index] = a^b^d^(a<<2)^(b<<18)^(c<<28);

	        return _state[_index];
        }
    }
        
    public struct DATA_BITSTRG
    {
        public _uint64[] w64ActiveChunk;
	    public bool		bActive;

    };
    
    public class CSecureVarBase
    {
        public int m_nDataType;

        protected int   	m_nSearchIndex = 0;
	    protected int		m_nOldRow = 0;
	    protected int		m_nShiftTimeSec;
	    protected int	    m_tLastClock;
	    protected bool		m_bInit = true;

	    protected const int	m_cstShiftTimeMin = 700;
	    protected const int	m_cstShiftTimeMax = 1500;

        protected DATA_BITSTRG[,] m_pstStrg;
        protected WellRng m_WellRng;


        public CSecureVarBase( )
        {
            Initialize();
        }

        protected void	Initialize( )
        {
            WellRng.WELLINIT();

            m_nShiftTimeSec = GetRandom( m_cstShiftTimeMin, m_cstShiftTimeMax );
	        m_tLastClock = GetTickTime( );

            AllocMem( );
        }

        protected int GetRandom(int nMin, int nMax)
        {
            return (int)(WellRng.WELLRNG512() % (nMax - nMin + 1) + nMin);
        }

        protected int GetTickTime()
        {
            return Environment.TickCount; 
        }

        protected bool AllocMem( )
        {
            m_pstStrg = new DATA_BITSTRG[Constants.STRG_LOW_NUM, Constants.STRG_COL_NUM];

            for (int i = 0; i < Constants.STRG_LOW_NUM; ++i)
            {
                for (int k = 0; k < Constants.STRG_COL_NUM; ++k )
                    m_pstStrg[i,k].w64ActiveChunk = new _uint64[Constants.CHUNK_NUM];
            }

            return true;
        }
        
	    protected void GetStrgIndexToSave( out int pi, out int pk, out int pk_old )
        {
            pi = Constants.INVALID_INDEX; pk = Constants.INVALID_INDEX; pk_old = Constants.INVALID_INDEX;

            int i=0, k=0;

            if (m_bInit)
            {
                i = 0;
                m_bInit = false;
            }
            else
            {
                int tCurrentTime = GetTickTime();

                if( tCurrentTime - m_tLastClock >= m_nShiftTimeSec)
                {
                    m_tLastClock = tCurrentTime;
                    m_nShiftTimeSec = GetRandom(m_cstShiftTimeMin, m_cstShiftTimeMax);

                    ShiftCurrentStorage(out i, out k);
                }
                else
                {
                    GetCurrentStrgIndex(out i, out k);
                }

                pk_old = k;
            }

            pi = i;
            pk = GetRandom(0, Constants.STRG_COL_NUM - 1);
        }

        protected void ShiftCurrentStorage(out int pNewRow, out int pCurColumn)
        {
            int nCurRow = 0, nNewRow = 0, k = 0;

            GetCurrentStrgIndex(out nCurRow, out k);

            int nCount = 0;
            while (++nCount <= 5)
            {
                nNewRow = GetRandom(0, Constants.STRG_LOW_NUM - 1);
                if (nCurRow != nNewRow && m_nOldRow != nNewRow)
                    break;
            }
            
            m_pstStrg[nNewRow, k].bActive = m_pstStrg[nCurRow, k].bActive;
            Buffer.BlockCopy(m_pstStrg[nCurRow, k].w64ActiveChunk, 0, m_pstStrg[nNewRow, k].w64ActiveChunk, 0, sizeof(_uint64) * Constants.CHUNK_NUM);

            for (int index = 0; index < Constants.STRG_COL_NUM; ++index)
            {
                m_pstStrg[nCurRow, index].bActive = false;
                Array.Clear(m_pstStrg[nCurRow, index].w64ActiveChunk, 0, Constants.CHUNK_NUM);
            }

            m_nOldRow = nCurRow;
            m_nSearchIndex = nNewRow;

            pNewRow = nNewRow;
            pCurColumn = k;
        }

	    protected void GetCurrentStrgIndex( out int pi, out int pk ) 
        {
            if (m_bInit)
            {
                pi = 0; pk = 0;
                return;
            }

            pi = Constants.INVALID_INDEX; pk = Constants.INVALID_INDEX;

            int n = m_nSearchIndex;

            for (int k = 0; k < Constants.STRG_COL_NUM; ++k)
            {
                if (m_pstStrg[n, k].bActive)
                {
                    pi = n;
                    pk = k;
                    return;
                }
            }

            for (int i = 0; i < Constants.STRG_LOW_NUM; ++i)
            {
                for (int k = 0; k < Constants.STRG_COL_NUM; ++k)
                {
                    if (m_pstStrg[i, k].bActive)
                    {
                        pi = i;
                        pk = k;
                        return;
                    }
                }
            }
        }	    
    };




    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //
    // class T		: data type	 ( int, long, float, double, ... )
    //
    public class CSecureVar<T> : CSecureVarBase where T  : IConvertible 
    {
        private _uint64[] _aw64ChunkAndBit = new _uint64[Constants.CHUNK_NUM] { 
            0x00000000000000FCUL,
            0x000000000000E003UL, 
            0x0000000000FE1F00UL,
	        0x0000C0FFFF010000UL,
	        0xFFFF3F0000000000UL 
        };

        public CSecureVar()
        {
        }

        public CSecureVar(T value)
        {
            Set(value);
        }

        public bool Set(T value)
        {
            int wTypeSize = Marshal.SizeOf( typeof(T) );

            if( wTypeSize > sizeof(_uint64) )
	            return false;

            _uint64 w64ExtVal = 0;


            if (typeof(T).Equals(typeof(float)) )            
            {                
                float fValue = Convert.ToSingle((object)value);             
                byte[] bytes = BitConverter.GetBytes(fValue);
                             
                uint w32Val = BitConverter.ToUInt32(bytes, 0);
                w64ExtVal = (_uint64)w32Val;
            }
            else if (typeof(T).Equals(typeof(double)))
            {
                double dValue = Convert.ToDouble((object)value);
                byte[] bytes = BitConverter.GetBytes(dValue);
                w64ExtVal = BitConverter.ToUInt64(bytes, 0);
            }
            else
                w64ExtVal = Convert.ToUInt64((object)value);         

            int i, k, old_k;

            GetStrgIndexToSave( out i, out k, out old_k );

            if (Constants.INVALID_INDEX != old_k)
	            m_pstStrg[i, old_k].bActive = false;
            
            for (int index = 0; index < Constants.CHUNK_NUM; ++index)
            {
                m_pstStrg[i, k].w64ActiveChunk[index] = w64ExtVal & _aw64ChunkAndBit[index];
            }

            m_pstStrg[i, k].bActive = true;

            return true;
        }

        public T Get()
        {
            int i, k;

            GetCurrentStrgIndex(out i, out k);

            _uint64 w64Value = 0;

            for (int index = 0; index < Constants.CHUNK_NUM; ++index)
            {
                w64Value = w64Value | m_pstStrg[i, k].w64ActiveChunk[index];
            }

            if (typeof(T).Equals(typeof(float)))
            {
                byte[] bytes = BitConverter.GetBytes(w64Value);

                float fVal = BitConverter.ToSingle(bytes, 0);

                return (T)Convert.ChangeType((object)fVal, typeof(T));
            }

            else if (typeof(T).Equals(typeof(double)) )
            {
                byte[] bytes = BitConverter.GetBytes(w64Value);

                double dVal = BitConverter.ToDouble(bytes, 0);

                return (T)Convert.ChangeType((object)dVal, typeof(T));
            }
            else
                return (T)Convert.ChangeType((object)w64Value, typeof(T));
        }        
    };
}
